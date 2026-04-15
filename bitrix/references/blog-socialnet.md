# Блог и комментарии в текущем core

> Reference для Bitrix-скилла. Загружай, когда задача связана с модулем `blog`, постами, комментариями, категориями/тегами, блоговыми компонентами, mail-to-comment, поисковой индексацией блога или условным socialnet-контуром.
>
> Audit note: в текущем проверенном core подтверждён модуль `blog` версии `24.300.100`. Модуль `socialnetwork` в `www/bitrix/modules` не найден, поэтому socialnet/livefeed-часть этого файла считай условной и подключай только при явном появлении модуля.

## Что реально активно в текущем core

Подтверждённый рабочий маршрут сейчас такой:

- `CBlogPost`
- `CBlogComment`
- `CBlogUser`
- `CBlogCategory`, `CBlogPostCategory`
- `CBlogSearch::OnSearchReindex`
- `Bitrix\Blog\Internals\MailHandler::handleReplyReceivedBlogPost`
- стандартные `blog.*` компоненты

Условный и отложенный маршрут:

- `socialnetwork`
- livefeed-индексация
- рассылка/широковещательные уведомления через `im` + `intranet` + `pull`
- forward-from-mail в новый пост

## D7-слой блога: читать можно, писать нельзя

В текущем core D7-таблицы блога существуют как read-model, а не как полноценный write API.

### `Bitrix\Blog\PostTable`

Подтверждено в `lib/post.php`:

- таблица `b_blog_post`
- `getUfId()` возвращает `BLOG_POST`
- есть поля `CODE`, `MICRO`, `DATE_PUBLISH`, `PUBLISH_STATUS`, `ENABLE_COMMENTS`, `NUM_COMMENTS`, `NUM_COMMENTS_ALL`, `VIEWS`, `HAS_SOCNET_ALL`, `HAS_TAGS`, `HAS_IMAGES`, `HAS_PROPS`, `HAS_COMMENT_IMAGES`, `TITLE`, `DETAIL_TEXT`, `CATEGORY_ID`, `BACKGROUND_CODE`
- `add()`, `update()`, `delete()` бросают `NotImplementedException("Use CBlogPost class.")`

### `Bitrix\Blog\CommentTable`

Подтверждено в `lib/comment.php`:

- таблица `b_blog_comment`
- `getUfId()` возвращает `BLOG_COMMENT`
- есть reference `POST => \Bitrix\Blog\Post`
- `add()`, `update()`, `delete()` бросают `NotImplementedException("Use CBlogComment class.")`

### Практическое правило

- D7 ORM используй для выборок, runtime, join-ов и аналитики
- запись, обновление и удаление делай через `CBlogPost`, `CBlogComment`, `CBlogUser`

```php
use Bitrix\Blog\PostTable;

$rows = PostTable::getList([
    'select' => ['ID', 'TITLE', 'DATE_PUBLISH', 'PUBLISH_STATUS', 'NUM_COMMENTS'],
    'filter' => [
        '=BLOG_ID' => 5,
        '=PUBLISH_STATUS' => BLOG_PUBLISH_STATUS_PUBLISH,
    ],
    'order' => ['DATE_PUBLISH' => 'DESC'],
    'limit' => 20,
])->fetchAll();
```

```php
Loader::includeModule('blog');

$postId = CBlogPost::Add([
    'BLOG_ID' => 5,
    'AUTHOR_ID' => $userId,
    'TITLE' => 'Новый пост',
    'DETAIL_TEXT' => '<p>Текст поста</p>',
    'DATE_PUBLISH' => date('d.m.Y H:i:s'),
    'PUBLISH_STATUS' => BLOG_PUBLISH_STATUS_PUBLISH,
    'ENABLE_COMMENTS' => 'Y',
]);

if (!$postId)
{
    global $APPLICATION;
    $exception = $APPLICATION->GetException();
    throw new \RuntimeException($exception ? $exception->GetString() : 'Blog post add failed');
}
```

## Legacy API, который в этом core остаётся основным

### Посты

```php
Loader::includeModule('blog');

$dbPosts = CBlogPost::GetList(
    ['DATE_PUBLISH' => 'DESC'],
    [
        'BLOG_ID' => 5,
        'PUBLISH_STATUS' => BLOG_PUBLISH_STATUS_PUBLISH,
        'ACTIVE' => 'Y',
    ],
    false,
    ['nPageSize' => 20],
    ['ID', 'BLOG_ID', 'AUTHOR_ID', 'TITLE', 'DATE_PUBLISH', 'NUM_COMMENTS']
);

while ($post = $dbPosts->Fetch())
{
    // ...
}

CBlogPost::Update($postId, [
    'TITLE' => 'Обновлённый заголовок',
    'DETAIL_TEXT' => '<p>Обновлённый текст</p>',
]);

CBlogPost::Delete($postId);
```

### Комментарии

```php
$commentId = CBlogComment::Add([
    'POST_ID' => $postId,
    'BLOG_ID' => 5,
    'AUTHOR_ID' => $userId,
    'POST_TEXT' => '<p>Текст комментария</p>',
    'TEXT_TYPE' => 'html',
    'DATE_CREATE' => date('d.m.Y H:i:s'),
    'PARENT_ID' => 0,
]);

if (!$commentId)
{
    throw new \RuntimeException('Blog comment add failed');
}

$dbComments = CBlogComment::GetList(
    ['DATE_CREATE' => 'ASC'],
    ['POST_ID' => $postId, 'BLOG_ID' => 5],
    false,
    ['nTopCount' => 50],
    ['ID', 'AUTHOR_ID', 'POST_TEXT', 'DATE_CREATE', 'PARENT_ID', 'PUBLISH_STATUS']
);
```

### Блог-пользователь

В текущем core подтверждён и legacy CRUD через `CBlogUser`, и D7 helper `Bitrix\Blog\BlogUser`.

```php
$blogUser = CBlogUser::GetByID($userId, BLOG_BY_USER_ID);

if (!$blogUser)
{
    $blogUserId = CBlogUser::Add([
        'USER_ID' => $userId,
        'ALIAS' => 'user_' . $userId,
    ]);
}
```

## `Bitrix\Blog\BlogUser` как cache/helper слой

`Bitrix\Blog\BlogUser` в текущем core нужен не для CRUD, а как сервис вокруг блог-пользователей:

- кеширует список пользователей по `blogId`
- умеет `setBlogId()`
- умеет `cleanCache($blogId = null)`
- отдаёт аватары в предопределённых размерах `COMMENT` и `POST`

Если задача про "почему старый аватар не меняется в комментариях" или "почему блог-пользователь не перечитался", сначала смотри этот cache/helper слой.

## Теги и категории блога

```php
$tagId = CBlogCategory::Add([
    'BLOG_ID' => 5,
    'NAME' => 'bitrix',
]);

CBlogPostCategory::Add([
    'BLOG_ID' => 5,
    'POST_ID' => $postId,
    'CATEGORY_ID' => $tagId,
]);
```

`CATEGORY_ID` у поста и отдельные связи через `CBlogPostCategory` в текущем core живут параллельно. Если нужно нормализовать/починить теги, не ограничивайся только одним из слоёв.

## Стандартные `blog.*` компоненты, подтверждённые в ядре

В текущем core реально присутствуют:

- `blog`
- `blog.blog`
- `blog.blog.draft`
- `blog.blog.edit`
- `blog.blog.favorite`
- `blog.blog.moderation`
- `blog.calendar`
- `blog.category`
- `blog.commented_posts`
- `blog.friends`
- `blog.group.blog`
- `blog.groups`
- `blog.info`
- `blog.menu`
- `blog.metaweblog`
- `blog.new_blogs`
- `blog.new_comments`
- `blog.new_posts`
- `blog.new_posts.list`
- `blog.popular_blogs`
- `blog.popular_posts`
- `blog.post`
- `blog.post.comment`
- `blog.post.comment.list`
- `blog.post.edit`
- `blog.post.trackback`
- `blog.post.trackback.get`
- `blog.rss`
- `blog.rss.all`
- `blog.rss.link`
- `blog.search`
- `blog.user`
- `blog.user.group`
- `blog.user.settings`
- `blog.user.settings.edit`

Если задача про типовой UI блога, сначала считай контракт именно из соответствующего `install/components/bitrix/blog.*`.

## Пинг, размеры изображений и системные util-методы

`Bitrix\Blog\Util` подтверждён в текущем core и даёт:

- `getImageMaxWidth()`
- `getImageMaxHeight()`
- `sendBlogPing($params)`

`sendBlogPing()`:

- использует опцию `blog/send_blog_ping`
- пытается получить `server_name` из сайта, `SITE_SERVER_NAME`, `main:server_name` или `$_SERVER["SERVER_NAME"]`
- в итоге вызывает `CBlog::sendPing(...)`

Если задача про "почему ping не уходит после публикации", сначала смотри не внешний сервис, а этот флаг и резолв `server_name`.

## Почтовые обработчики, которые реально есть

В `install/index.php` подтверждены обработчики:

- `mail:onReplyReceivedBLOG_POST -> Bitrix\Blog\Internals\MailHandler::handleReplyReceivedBlogPost`
- `mail:onForwardReceivedBLOG_POST -> Bitrix\Blog\Internals\MailHandler::handleForwardReceivedBlogPost`

### Reply from mail -> новый комментарий

`handleReplyReceivedBlogPost()` в текущем core:

- получает `site_id`, `entity_id`, `from`, `content`, `attachments`
- валидирует сообщение и автора
- ищет пост через `CBlogPost::getList(...)`
- считает права через `CBlogPost::getSocNetPostPerms()` и `CBlogComment::getSocNetUserPerms()`
- проверяет дубль через `Bitrix\Blog\Item\Comment::checkDuplicate(...)`
- выбирает UF-код для файлов: `UF_BLOG_COMMENT_FILE` или `UF_BLOG_COMMENT_DOC`
- сохраняет вложения через `CSocNetLogComponent::saveFileToUF(...)`
- может поставить `PUBLISH_STATUS = BLOG_PUBLISH_STATUS_READY` при premoderate
- в конце создаёт комментарий через `CBlogComment::add(...)`

Это важный реальный маршрут. Если задача про email-reply в блог, не нужно придумывать кастомный парсер с нуля, пока не проверен этот core handler.

### Forward from mail -> новый пост

`handleForwardReceivedBlogPost()` существует, но требует `Loader::includeModule('socialnetwork')`. Если модуля нет, он бросает `SystemException`.

Для текущего audited core этот путь считай deferred.

## Поисковая индексация и module events

Подтверждённые зависимости модуля в `install/index.php`:

- `search:OnReindex -> CBlogSearch::OnSearchReindex`
- `main:OnUserDelete -> Bitrix\Blog\BlogUser::onUserDelete`
- `main:OnSiteDelete -> CBlogSitePath::DeleteBySiteID`
- mail handlers для reply/forward

Следствие: после нестандартных массовых правок постов/комментариев не забывай про поисковый индекс блога, а не только про саму таблицу.

## Broadcast и livefeed-index классы: существуют, но сейчас условны

В текущем core реально есть:

- `Bitrix\Blog\Broadcast`
- `Bitrix\Blog\Update\LivefeedIndexPost`
- `Bitrix\Blog\Update\LivefeedIndexComment`

Но они завязаны на соседние модули и опции:

- `Broadcast` использует `im`, `intranet`, `pull` и данные `PostSocnetRights`
- steppers смотрят `Option::get('blog', 'needLivefeedIndexPost', 'Y')` и `needLivefeedIndexComment`

Пока `socialnetwork` в core отсутствует, эти сценарии не делай основным маршрутом задачи.

## Что делать с socialnet-частью

Пока `socialnetwork` отсутствует:

- не веди задачу в `CSocNet*`
- не описывай livefeed как гарантированно рабочий слой
- не предлагай forward-to-post, широковещательные уведомления и livefeed indexing как основной сценарий

Если модуль появится позже, этот reference можно снова расширять socialnet-контуром уже по живому core.

## Gotchas

- `PostTable::add/update/delete()` и `CommentTable::add/update/delete()` в текущем core не поддержаны и специально бросают `NotImplementedException`.
- UF-коды важны: `BLOG_POST` и `BLOG_COMMENT` нужны для UF и файловых вложений.
- Маршрут "ответ письмом -> комментарий" уже есть в core. Не надо дублировать его без необходимости.
- Поиск по блогу завязан на `CBlogSearch::OnSearchReindex`, поэтому массовые изменения без переиндексации могут дать расхождение "в базе есть, в поиске нет".
- `socialnet`-логика в этом файле сейчас намеренно вторична: модуль отсутствует в проверенном ядре.
