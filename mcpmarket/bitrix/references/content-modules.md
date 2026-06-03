# Content Modules
> MCP Market compact bundle. Source files are concatenated from `bitrix/references/*` to keep the imported skill folder below the 50-file limit.

---

## Source: `blog-socialnet.md`

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

## Stock template layer, если `local/*` отсутствует

В текущем checkout нет `www/local`, поэтому для блоговых задач следующим truth layer после module API становятся stock component templates самого core.

Подтверждённые template-ветки:

- у агрегирующего `bitrix:blog` есть `.default`, `general_page`, `one_blog`, `one_blog_with_main_page`, а также legacy `old_version`
- у `bitrix:blog.post` есть `.default` и `micro`
- у `bitrix:blog.post.edit` есть `.default` и `micro`
- у ряда компонентов есть отдельные `old_version` templates
- у `bitrix:blog.category` есть template `socialnetwork`

Практическое следствие: когда в проекте нет `local/components`, надо аудировать не только `component.php`, но и конкретный stock template variant, который реально используется.

## Где у шаблонов блога лежит логика, кроме `template.php`

Это особенно важно для `bitrix:blog.post.edit`:

- в `.default` подтверждён `result_modifier.php`
- там же есть `script.php`, `script.js`, `neweditor.php`, `style.css`
- в `micro`-ветке подтверждены отдельные `template.php`, `script.js`, `lhe.php`

То есть шаблонный слой здесь не сводится к одной вёрстке.

Дополнительно подтверждено:

- `result_modifier.php` в `.default` подключает resize/upload обработчик через `main.file.input.upload`
- `micro` template использует `bitrix:main.userconsent.request`
- `micro` template умеет тянуть `bitrix:socialnetwork.group.selector`, если разрешён групповой постинг
- `blog.category/templates/socialnetwork` прямо подключает CSS socialnetwork-компонентов

Если модуль `socialnetwork` в проекте отсутствует, template `socialnetwork` и socialnetwork-фрагменты внутри micro-режима считай условными.

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
- При отсутствии `local/*` следующий truth layer для блога — stock templates компонента, включая `micro`, `old_version` и `socialnetwork`-ветки.
- В `blog.post.edit` и соседних шаблонах логика живёт не только в `template.php`, но и в `result_modifier.php`, JS и upload hooks.

---

## Source: `forum.md`

# Форумы (модуль forum)

> Audit note: ниже сверено с текущим `www/bitrix/modules/forum`. Подтверждены legacy-классы `CForumNew`, `CForumTopic`, `CForumMessage`, `CForumUser`, `CForumSubscribe`, а также D7-таблицы `\Bitrix\Forum\ForumTable`, `TopicTable`, `MessageTable`, `UserTable`. Подтверждены стандартные компоненты `bitrix:forum`, `bitrix:forum.topic.list`, `bitrix:forum.topic.read`, `bitrix:forum.post_form`, `bitrix:forum.comments`, `bitrix:forum.search`, `bitrix:forum.subscribe.list`, `bitrix:forum.pm.*`.

## Архитектура

В текущем core форумный модуль двухслойный:

- write-path и большая часть стандартных компонентов опираются на legacy `CForum*`
- read-side, отчёты и выборки можно делать через D7-таблицы `\Bitrix\Forum\*Table`

Практическое правило:

- если меняешь форум, тему, сообщение или подписку в потоке стандартного UI, сначала смотри `CForum*`
- если строишь выборку, отчёт, background-диагностику или сервисный слой, смотри D7-таблицы

---

## Форумы: CForumNew

Подтверждены методы:

- `CForumNew::Add`
- `CForumNew::Update`
- `CForumNew::Delete`
- `CForumNew::GetList`
- `CForumNew::GetByID`
- `CForumNew::SetAccessPermissions`
- `CForumNew::GetAccessPermissions`

```php
use Bitrix\Main\Loader;

Loader::includeModule('forum');

$forumId = CForumNew::Add([
    'NAME' => 'Техподдержка',
    'DESCRIPTION' => 'Основной форум проекта',
    'SORT' => 100,
    'ACTIVE' => 'Y',
    'SITES' => [
        SITE_ID => '/forum/read.php?FID=#FORUM_ID#&TID=#TOPIC_ID#&MID=#MESSAGE_ID##message#MESSAGE_ID#',
    ],
]);

if (!$forumId) {
    global $APPLICATION;
    $exception = $APPLICATION->GetException();
    throw new \RuntimeException($exception ? $exception->GetString() : 'Forum add failed');
}

CForumNew::SetAccessPermissions($forumId, [
    2 => 'E', // все пользователи
    1 => 'Y', // администраторы
]);

$forum = CForumNew::GetByID($forumId);
```

> `SITES` в текущем core важен не только для привязки сайта, но и для построения canonical forum URL внутри модуля.

---

## Темы и сообщения

Подтверждены методы:

- `CForumTopic::Add/Update/Delete/GetList/GetByID`
- `CForumMessage::Add/Update/Delete/GetList/GetByID`
- `CForumUser::Add/Update/Delete/GetByID`
- `CForumSubscribe::Add/Update/Delete/GetList`

```php
Loader::includeModule('forum');

$topics = CForumTopic::GetList(
    ['LAST_POST_DATE' => 'DESC'],
    ['FORUM_ID' => $forumId, 'APPROVED' => 'Y'],
    false,
    20
);

while ($topic = $topics->Fetch()) {
    echo $topic['TITLE'] . PHP_EOL;
}

$messages = CForumMessage::GetList(
    ['ID' => 'ASC'],
    ['TOPIC_ID' => $topicId, 'APPROVED' => 'Y'],
    false,
    50,
    ['GET_TOPIC_INFO' => 'N', 'GET_FORUM_INFO' => 'N']
);

while ($message = $messages->Fetch()) {
    echo $message['POST_MESSAGE'] . PHP_EOL;
}
```

Программное добавление сообщения делай через `CForumMessage::Add`, если хочешь получить штатное поведение:

- фильтрацию текста
- обработку файлов
- обновление статистики
- поисковую индексацию
- события `onBeforeMessageAdd` / `onAfterMessageAdd`

---

## D7-таблицы

Подтверждены:

- `\Bitrix\Forum\ForumTable`
- `\Bitrix\Forum\TopicTable`
- `\Bitrix\Forum\MessageTable`
- `\Bitrix\Forum\UserTable`

```php
use Bitrix\Forum\MessageTable;
use Bitrix\Main\Loader;

Loader::includeModule('forum');

$result = MessageTable::getList([
    'select' => ['ID', 'TOPIC_ID', 'FORUM_ID', 'AUTHOR_ID', 'POST_DATE', 'APPROVED'],
    'filter' => ['=FORUM_ID' => $forumId],
    'order' => ['ID' => 'DESC'],
    'limit' => 20,
]);

while ($row = $result->fetch()) {
    var_dump($row);
}
```

D7-таблицы здесь особенно полезны для:

- выборок без тяжёлого компонентного слоя
- admin/report сценариев
- диагностики счётчиков и статусов
- пакетного анализа данных

---

## Стандартные компоненты

В текущем core подтверждены типовые маршруты:

- `bitrix:forum`
- `bitrix:forum.topic.list`
- `bitrix:forum.topic.read`
- `bitrix:forum.post_form`
- `bitrix:forum.comments`
- `bitrix:forum.search`
- `bitrix:forum.subscribe.list`
- `bitrix:forum.pm.edit`
- `bitrix:forum.pm.list`
- `bitrix:forum.pm.read`

Для кастомизации сначала смотри:

1. `www/bitrix/modules/forum/install/components/bitrix/<component>/component.php`
2. `.parameters.php`
3. шаблон компонента
4. только потом проектный override

---

## Права и действия пользователя

Подтверждены проверки:

- `CForumNew::CanUserViewForum`
- `CForumNew::CanUserAddForum`
- `CForumNew::CanUserUpdateForum`
- `CForumNew::CanUserDeleteForum`
- `CForumNew::CanUserModerateForum`
- `CAllForumMessage::CanUserAddMessage/CanUserUpdateMessage/CanUserDeleteMessage`

Если задача звучит как:

- “почему пользователь видит форум, но не может писать”
- “почему нельзя отредактировать сообщение”
- “почему тема есть в админке, но не видна на сайте”

то сначала проверь:

1. `ACTIVE` у форума/темы/сообщения
2. permission letter для групп
3. статус `APPROVED`
4. сайты в `SITES`
5. кеш и поисковую индексацию

---

## Gotchas

- Форумный UI в этом core всё ещё очень legacy-heavy. Не пытайся насильно перевести всё на D7, если задача живёт внутри стандартного компонента.
- `CForumMessage::Add` делает много побочных действий: файлы, статистика, поиск, события. Если обойти его прямым SQL или голой `MessageTable::add`, легко сломать счётчики и выдачу.
- Для чтения и отчётов D7 удобнее, для штатной мутации часто безопаснее legacy.
- Форумные URL и доступ завязаны на `SITES` и permission letters, а не только на ID сущности.

---

## Source: `vote.md`

# Голосования и опросы (модуль vote)

> Audit note: ниже сверено с текущим `www/bitrix/modules/vote`. Подтверждены legacy-классы `CVote`, `CVoteChannel`, `CVoteQuestion`, `CVoteAnswer`, `CVoteEvent`, `CVoteUser`, а также D7-таблицы `\Bitrix\Vote\VoteTable`, `ChannelTable`, `QuestionTable`, `AnswerTable`. Подтверждены стандартные компоненты `bitrix:voting.form`, `bitrix:voting.current`, `bitrix:voting.result`, `bitrix:voting.list`, `bitrix:voting.attached.result`, `bitrix:voting.uf`.

## Архитектура

Как и `forum`, модуль `vote` в текущем core гибридный:

- базовый CRUD и типовой UI опираются на `CVote*`
- для чтения, отчётов и служебных выборок можно использовать D7-таблицы `\Bitrix\Vote\*Table`

---

## Vote, Channel, Question, Answer

Подтверждены методы:

- `CVote::Add/Update/Delete/Reset/GetList`
- `CVoteChannel::Add/Update/Delete/GetList`
- `CVoteQuestion::Add/Update/Delete/Reset/GetList`
- `CVoteAnswer::Add/Update/Delete/GetList`
- `CVoteEvent::GetList/Delete`

```php
use Bitrix\Main\Loader;

Loader::includeModule('vote');

$votes = CVote::GetList(
    's_id',
    'desc',
    ['ACTIVE' => 'Y']
);

while ($vote = $votes->Fetch()) {
    echo $vote['TITLE'] . PHP_EOL;
}

$questions = CVoteQuestion::GetList(
    $voteId,
    's_c_sort',
    'asc'
);

while ($question = $questions->Fetch()) {
    $answers = CVoteAnswer::GetList(
        $question['ID'],
        's_c_sort',
        'asc'
    );

    while ($answer = $answers->Fetch()) {
        echo $answer['MESSAGE'] . PHP_EOL;
    }
}
```

Если задача связана с реальным изменением структуры опроса, основной write-path здесь:

- `CVote::Add/Update/Delete`
- `CVoteQuestion::Add/Update/Delete`
- `CVoteAnswer::Add/Update/Delete`

Эти методы уже знают про:

- валидацию полей
- загрузку изображений
- события модуля `vote`
- reset результатов и каскадные удаления

---

## D7-таблицы

Подтверждены:

- `\Bitrix\Vote\VoteTable`
- `\Bitrix\Vote\ChannelTable`
- `\Bitrix\Vote\QuestionTable`
- `\Bitrix\Vote\AnswerTable`

```php
use Bitrix\Main\Loader;
use Bitrix\Vote\VoteTable;

Loader::includeModule('vote');

$result = VoteTable::getList([
    'select' => ['ID', 'TITLE', 'CHANNEL_ID', 'ACTIVE', 'TIMESTAMP_X'],
    'filter' => ['=ACTIVE' => 'Y'],
    'order' => ['ID' => 'DESC'],
]);

while ($row = $result->fetch()) {
    var_dump($row);
}
```

Подход:

- D7 — для выборок, диагностики, background-аналитики
- legacy `CVote*` — для пользовательского CRUD и сценариев, совпадающих со стандартной админкой

---

## Стандартные компоненты

Подтверждены:

- `bitrix:voting.form`
- `bitrix:voting.current`
- `bitrix:voting.result`
- `bitrix:voting.list`
- `bitrix:voting.attached.result`
- `bitrix:voting.uf`

Для задач на фронте обычно сначала смотри:

1. `voting.form`
2. `voting.current`
3. `voting.result`

А уже потом решай, нужен ли custom component/template.

---

## События и служебные сценарии

В текущем core подтверждены типовые события до/после CRUD:

- `onBeforeVoteDelete` / `onAfterVoteDelete`
- `onBeforeVoteQuestionAdd` / `onAfterVoteQuestionAdd`
- `onBeforeVoteQuestionUpdate` / `onAfterVoteQuestionUpdate`
- `onBeforeVoteAnswerAdd` / `onAfterVoteAnswerAdd`
- `onBeforeVoteAnswerUpdate` / `onAfterVoteAnswerUpdate`

Это удобный слой для:

- валидации структуры голосования
- логирования
- интеграции с собственными таблицами
- синхронизации attached-vote сценариев

---

## Gotchas

- Не обходи `CVote::Delete` прямым удалением из таблиц: там есть каскад по вопросам, ответам, событиям и attached vote.
- Для attached/UF-сценариев сначала смотри `bitrix:voting.attached.result` и `bitrix:voting.uf`, а не собирай UI с нуля.
- Если в задаче есть “сбросить результаты”, у `CVote::Reset` и `CVoteQuestion::Reset` уже есть штатный путь.

---

## Source: `webforms.md`

# Веб-формы и результаты в текущем core

> Reference для Bitrix-скилла. Загружай, когда задача связана с модулем `form`, формами, вопросами и ответами, результатами, статусами, почтовыми шаблонами, validators, CRM link, secure file download или стандартными `form.*` компонентами.
>
> Audit note: проверено по текущему core `form` версии `25.0.0` через `install/index.php`, `install/components`, `install/tools`, `classes/general/*` и `classes/mysql/*`.

```php
use Bitrix\Main\Loader;

Loader::includeModule('form');
```

## Что реально есть в модуле `form`

В текущем core модуль `form` значительно шире, чем "просто отправить письмо":

- формы и их структура: `CForm`
- результаты: `CFormResult`
- поля/вопросы: `CFormField`
- варианты ответов: `CFormAnswer`
- статусы: `CFormStatus`
- валидаторы: `CFormValidator`
- CRM связка: `CFormCrm`
- стандартные компоненты `form.*`
- безопасная отдача файлов по hash
- status handlers до/после смены статуса

Если задача требует права, workflow статусов, повторное редактирование, CRM или безопасную выдачу файлов, это маршрут точно в `form`, а не в "простую форму на инфоблоке".

## Подтверждённые стандартные компоненты

В текущем ядре есть:

- `bitrix:form`
- `bitrix:form.result.new`
- `bitrix:form.result.edit`
- `bitrix:form.result.view`
- `bitrix:form.result.list`
- `bitrix:form.result.list.my`

Если задача упирается в типовой UI формы/результатов, сначала считай контракт стандартного компонента, а потом уже проектный шаблон.

## Stock component/template layer, если `local/*` отсутствует

В текущем checkout нет `www/local`, поэтому у форм следующий truth layer после module API — это stock components и их templates.

Подтверждено:

- `bitrix:form.result.new` имеет `.default`
- `bitrix:form.result.edit` имеет `.default`
- `bitrix:form.result.list` имеет `.default` и `intranet`
- `bitrix:form.result.view` имеет `.default` и `intranet`
- `bitrix:form.result.list.my` имеет `.default`
- `bitrix:form` имеет `.default`

Если нет project override-слоя, надо смотреть сразу три места:

- `component.php`
- конкретный template variant
- `style.css` и соседние assets компонента

## Что делает `form.result.new` на уровне компонента

В `component.php` у `bitrix:form.result.new` подтверждены важные нефронтовые вещи:

- `WEB_FORM_ID` может резолвиться по SID через `CForm::GetBySID()`
- компонент отключает кеш на POST и на `formresult=ADDOK`
- при кешировании регистрирует теги `forms` и `form_<ID>`
- поддерживает `IGNORE_CUSTOM_TEMPLATE = N` и умеет уходить в шаблон формы из настроек самой формы
- на ошибках подключает `error.css`

Следствие: диагностика формы не сводится к `template.php`. Иногда проблема лежит в component-level cache, разрешении custom template или в самом `component.php`.

## Когда брать `form`, а когда достаточно инфоблока

| Подход | Когда использовать |
|--------|--------------------|
| `form` | Нужны вопросы/ответы, статусы, права, редактирование результата, почтовые шаблоны, админский список, validators, CRM-link |
| Инфоблок или свой D7 controller | Нужен простой lead-capture без workflow и без штатной form-админки |

## Формы и права

Подтверждённые методы верхнего слоя:

- `CForm::GetList()`
- `CForm::GetByID()`
- `CForm::GetBySID()`
- `CForm::GetDataByID()`
- `CForm::Set()`
- `CForm::Copy()`
- `CForm::Delete()`
- `CForm::Reset()`
- `CForm::SetMailTemplate()`
- `CForm::GetPermission()`
- `CForm::GetPermissionList()`

`CForm::GetPermissionList()` в текущем core возвращает уровни:

- `1` — denied
- `10` — fill
- `15` — fill + edit own results
- `20` — view results
- `25` — view results with additional params
- `30` — full write/admin on form

```php
$permission = CForm::GetPermission($formId);

if ($permission < 10)
{
    throw new \RuntimeException('Недостаточно прав для заполнения формы');
}
```

## Получить форму и её структуру

```php
$forms = CForm::GetList(
    $by = 's_sort',
    $order = 'asc',
    ['ACTIVE' => 'Y']
);

while ($form = $forms->Fetch())
{
    // $form['ID'], $form['SID'], $form['NAME']
}
```

```php
$arForm = $arQuestions = $arAnswers = $arDropDown = $arMultiSelect = [];

CForm::GetDataByID(
    $formId,
    $arForm,
    $arQuestions,
    $arAnswers,
    $arDropDown,
    $arMultiSelect,
    'N',
    'N'
);
```

`CForm::GetDataByID()` остаётся основным способом получить полноценную структуру формы с вопросами и вариантами ответов.

## Результаты: базовый lifecycle

Подтверждённые методы `CFormResult`:

- `GetList()`
- `GetByID()`
- `GetPermissions()`
- `GetFileByAnswerID()`
- `GetFileByHash()`
- `SetEvent()`
- `GetDataByID()`
- `GetDataByIDForHTML()`
- `Add()`
- `Update()`
- `SetField()`
- `Delete()`
- `Reset()`
- `SetStatus()`
- `Mail()`
- `SetCRMFlag()`

### Создать результат

```php
global $strError;

$resultId = CFormResult::Add(
    $formId,
    $_POST,
    'Y',
    false
);

if ((int)$resultId <= 0)
{
    throw new \RuntimeException($strError ?: 'Не удалось сохранить результат формы');
}

CFormResult::Mail($resultId);
```

### Получить список результатов

```php
$isFiltered = false;

$dbResults = CFormResult::GetList(
    $formId,
    $by = 's_timestamp',
    $order = 'desc',
    ['STATUS_ID' => 1],
    $isFiltered,
    'Y',
    false
);

while ($row = $dbResults->Fetch())
{
    $resultMeta = [];
    $answers = [];

    CFormResult::GetDataByID($row['ID'], [], $resultMeta, $answers);
}
```

### Обновить отдельные поля результата

`CFormResult::SetField()` в текущем core:

- отдельно обрабатывает additional fields
- умеет file/image answers
- пишет `USER_FILE_HASH`
- обновляет поисковые поля `ANSWER_TEXT_SEARCH`, `ANSWER_VALUE_SEARCH`, `USER_TEXT_SEARCH`

Если задача про "дописать одно поле в существующий результат" или "обновить файл без полной перезаписи результата", смотри сюда, а не только в `Update()`.

## Статусы и status handlers

Подтверждённые методы `CFormStatus`:

- `GetList()`
- `GetByID()`
- `GetPermissionList()`
- `GetPermissions()`
- `GetDefault()`
- `Set()`
- `Delete()`
- `Copy()`
- `SetMailTemplate()`

Статусные permission buckets в текущем core:

- `VIEW`
- `MOVE`
- `EDIT`
- `DELETE`

```php
$defaultStatusId = CFormStatus::GetDefault($formId);

CFormResult::SetStatus($resultId, $defaultStatusId);
```

### Что происходит при смене статуса

`CFormResult::SetStatus()` в текущем core:

- проверяет права на форму и результат
- проверяет право перемещения в новый статус
- вызывает `onBeforeResultStatusChange`
- запускает `CForm::ExecHandlerBeforeChangeStatus(..., "SET_STATUS", $NEW_STATUS_ID)`
- сохраняет статус
- вызывает `onAfterResultStatusChange`
- запускает `CForm::ExecHandlerAfterChangeStatus(..., "SET_STATUS")`

### `HANDLER_OUT` / `HANDLER_IN`

У статусов реально есть поля:

- `HANDLER_OUT`
- `HANDLER_IN`

`CForm::ExecHandlerBeforeChangeStatus()` и `ExecHandlerAfterChangeStatus()` включают эти PHP-файлы из document root. Это не абстрактные callbacks в БД, а реальный `include` файловой логики.

Следствие: задачи по status handlers надо вести как аудит PHP-файлов и их side effects, а не как "настройку строки в админке".

## События результата, удаления и reset

Важные подтверждённые точки lifecycle:

- `Delete()` вызывает `onBeforeResultDelete`
- `Delete()` запускает `CForm::ExecHandlerBeforeChangeStatus($RESULT_ID, "DELETE")`
- `SetStatus()` вызывает `onBeforeResultStatusChange` и `onAfterResultStatusChange`
- `Reset()` умеет очищать ответы выборочно
- `Reset()` умеет не трогать additional fields, если явно не просили `DELETE_ADDITIONAL = "Y"`

Если задача про "частично очистить результат" или "не потерять служебные поля", сначала смотри `Reset()`, а не делай `Delete()+Add()`.

## Почта и site binding

`CFormResult::Mail($RESULT_ID, $TEMPLATE_ID = false)` подтверждён в текущем core.

Важно: внутри `Mail()` есть проверка, что текущий `SITE_ID` входит в список сайтов формы. Если форма привязана не к тому сайту, письма могут "молча" не уйти.

Это один из первых пунктов диагностики для задачи "результат сохранился, но письмо не отправилось".

## Валидаторы

Подтверждённый validator-layer:

- `CFormValidator::GetList()`
- `CFormValidator::GetListForm()`
- `CFormValidator::GetAllList()`
- `CFormValidator::Execute()`
- `CFormValidator::Set()`
- `CFormValidator::SetBatch()`

Реестр валидаторов собирается через module events:

- `GetModuleEvents("form", "onFormValidatorBuildList", true)`

В текущем core уже есть встроенные validator-ы в `modules/form/validators/*`, включая:

- длину текста
- числовые диапазоны
- INN
- размер файла
- тип файла
- размер изображения
- возраст/дату

Если задача про кастомный validator, его надо проектировать как event-driven descriptor с `HANDLER`, а не как произвольную if-ветку в шаблоне формы.

## CRM link

Подтверждённый CRM-layer живёт в `CFormCrm`:

- `GetByID()`
- `GetByFormID()`
- `GetFields()`
- `SetForm()`
- `onResultAdded()`
- `AddLead()`

Типы связи:

- `CFormCrm::LINK_AUTO = 'A'`
- `CFormCrm::LINK_MANUAL = 'M'`

`SetForm()` в текущем core умеет:

- сохранять link формы к CRM-коннектору
- строить field mapping
- при необходимости автоматически создавать form field под CRM field

`onResultAdded()` автоматически вызывает `AddLead()` только для `LINK_AUTO`.

Если задача про "почему лид не улетает после отправки формы", сначала проверь:

- есть ли link у формы
- какой `LINK_TYPE`
- какие поля реально сматчены

## Файлы и безопасная выдача

Подтверждённые методы:

- `CFormResult::GetFileByAnswerID($RESULT_ID, $ANSWER_ID)`
- `CFormResult::GetFileByHash($RESULT_ID, $HASH)`

`GetFileByHash()` в текущем core отдаёт файл только если:

- право на форму `>= 20`
- или право `>= 15` и текущий пользователь владелец результата

Также в модуле есть:

- `install/tools/form_show_file.php`

Но это только wrapper на:

- `/bitrix/modules/form/admin/form_show_file.php`

Если задача про публичную выдачу вложения формы по hash, не ломай этот security-layer ручным `CFile::GetFileArray()` без проверки прав.

## Что учитывать в template variants `list` и `view`

У `form.result.list` и `form.result.view` подтверждены отдельные templates `intranet`.

Практический вывод:

- если список/просмотр результата "выглядит не как .default", это может быть штатный intranet-template, а не проектный override
- проверяй template variant до того, как объявлять поведение кастомным
- у `form.result.list/templates/intranet/template.php` есть отдельная filter/list UI-логика, включая cookie-состояние фильтра и массовые действия

## Sender и соседние интеграции

В `install/index.php` подтверждена зависимость:

- `sender:OnConnectorList -> Bitrix\Form\SenderEventHandler::onConnectorListForm`

То есть модуль `form` умеет встраиваться в контур `sender`, но это соседний integration point, а не основная модель формы. Если `sender` не участвует в задаче, не тащи его туда без необходимости.

## Простейший fallback без `form`

Если нужен только лёгкий lead-capture без workflow, прав и статусной машины, действительно можно использовать инфоблок или свой D7 controller. Но это отдельный маршрут, а не замена возможностей `form`.

## Gotchas

- Не своди `form` к одной операции `CFormResult::Add()`: в реальном core здесь есть статусы, handlers, validators, CRM, secure files и права.
- `CFormResult::Mail()` зависит от привязки формы к `SITE_ID`.
- `GetFileByHash()` уже содержит permission-логику. Не обходи её самописной выдачей файла.
- Status handlers выполняют PHP-файлы с диска. Их надо ревьюить как код с побочными эффектами.
- `Reset()` и `Delete()` ведут себя по-разному; для частичного очищения результата не подменяй одно другим.
- При отсутствии `local/*` следующий truth layer для form-задач — stock component.php, template variant и component assets, а не только одна `.default`-вёрстка.
- `form.result.new` и `form.result.edit` имеют собственный error-style слой и component-level cache rules, которые часто важнее шаблонной косметики.

---

## Source: `mail-notifications.md`

# Почтовые события и уведомления

> Reference для Bitrix-скилла. Загружай когда задача связана с `CEvent`, `Bitrix\Main\Mail\Event`, шаблонами почтовых событий или перехватом отправки. Если задача уже про SMS-провайдера, ограничения, callback-и, sender management или REST-интеграцию, дополнительно загружай `messageservice.md`: это отдельный модульный слой, а не просто расширение mail-событий. Если задача shop-specific про рассылки, сегменты, клики/opens, отписки, sender triggers или report/statistic side effects, дополнительно загружай `shop-marketing-analytics.md`.
>
> Audit note: проверено по текущему core `main/lib/mail/event.php`, `main/classes/general/event.php`.

## Архитектура

В текущем core цепочка такая:

1. **Тип события** (`b_event_type`) — описание полей и типа доставки
2. **Шаблон сообщения** (`b_event_message`) — текст, тема, сайты
3. **Очередь** (`b_event`) — запись на отправку

`Bitrix\Main\Mail\Event::send()` пишет в очередь.  
`Bitrix\Main\Mail\Event::sendImmediate()` отправляет сразу.

Legacy-обёртка:

- `CEvent::Send()` -> возвращает ID записи в очереди или `false`
- `CEvent::SendImmediate()` -> возвращает строковый статус отправки

---

## Создание типа почтового события

```php
use Bitrix\Main\Mail\Internal\EventTypeTable;

$exists = EventTypeTable::getList([
    'filter' => [
        '=EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
        '=LID' => 'ru',
    ],
])->fetch();

if (!$exists)
{
    CEventType::Add([
        'EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
        'LID' => 'ru', // язык, не SITE_ID
        'NAME' => 'Новый заказ',
        'DESCRIPTION' => "Поля:\n#ORDER_ID#\n#EMAIL#\n#TOTAL#",
        'SORT' => 100,
        'EVENT_TYPE' => EventTypeTable::TYPE_EMAIL, // или TYPE_SMS
    ]);
}
```

---

## Создание шаблона письма

```php
$eventMessage = new CEventMessage();

$messageId = $eventMessage->Add([
    'EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
    'LID' => ['s1'],
    'ACTIVE' => 'Y',
    'EMAIL_FROM' => '#EMAIL_FROM#',
    'EMAIL_TO' => '#EMAIL#',
    'SUBJECT' => 'Ваш заказ #ORDER_ID# принят',
    'MESSAGE' => "Здравствуйте!\nЗаказ №#ORDER_ID# на сумму #TOTAL# принят.",
    'BODY_TYPE' => 'text',
]);
```

---

## Отправка события

### Через очередь

```php
use Bitrix\Main\Mail\Event;

$result = Event::send([
    'EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
    'LID' => SITE_ID,
    'FIELDS' => [
        'ORDER_ID' => $orderId,
        'EMAIL' => $email,
        'TOTAL' => $total,
    ],
]);

if (!$result->isSuccess())
{
    // ошибки записи в очередь
}
```

### Немедленно

```php
use Bitrix\Main\Mail\Event;

$sendResult = Event::sendImmediate([
    'EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
    'LID' => SITE_ID,
    'FIELDS' => [
        'ORDER_ID' => $orderId,
        'EMAIL' => $email,
    ],
]);
```

Подтверждённые статусы `sendImmediate()`:

- `Event::SEND_RESULT_SUCCESS` = `'Y'`
- `Event::SEND_RESULT_ERROR` = `'F'`
- `Event::SEND_RESULT_PARTLY` = `'P'`
- `Event::SEND_RESULT_TEMPLATE_NOT_FOUND` = `'0'`
- `Event::SEND_RESULT_NONE` = `'N'`

### Legacy API

```php
$queueId = CEvent::Send(
    'MY_MODULE_ORDER_NEW',
    SITE_ID,
    [
        'ORDER_ID' => $orderId,
        'EMAIL' => $email,
    ]
);
```

`$queueId` здесь будет ID записи в очереди или `false`.

---

## Отправка с вложением

```php
use Bitrix\Main\Mail\Event;

Event::send([
    'EVENT_NAME' => 'MY_MODULE_ORDER_NEW',
    'LID' => SITE_ID,
    'FIELDS' => [
        'ORDER_ID' => $orderId,
        'EMAIL' => $email,
    ],
    'FILE' => [
        $fileId,
        '/path/to/file.pdf',
    ],
]);
```

---

## Прямое письмо без события

```php
use Bitrix\Main\Mail\Mail;

Mail::send([
    'TO' => 'user@example.com',
    'FROM' => 'noreply@example.com',
    'SUBJECT' => 'Тема письма',
    'BODY' => '<b>HTML-тело</b>',
    'CONTENT_TYPE' => 'html',
    'CHARSET' => 'UTF-8',
    'HEADER' => ['X-Custom-Header: value'],
]);
```

---

## `OnBeforeEventSend`

Регистрация:

```php
use Bitrix\Main\EventManager;

EventManager::getInstance()->addEventHandler(
    'main',
    'OnBeforeEventSend',
    [MyModule\EventHandler::class, 'onBeforeEventSend']
);
```

Обработчик:

```php
class EventHandler
{
    public static function onBeforeEventSend(
        array &$fields,
        array &$eventMessage,
        $context,
        array &$result
    )
    {
        $fields['EXTRA_INFO'] = '...';

        if (($fields['EMAIL'] ?? '') === 'blocked@example.com')
        {
            return false;
        }

        return null;
    }
}
```

Что подтверждено по текущему core:

- обработчик вызывается с `(&$arFields, &$eventMessage, $context, &$arResult)`
- если обработчик вернул `false`, текущий шаблон пропускается через `continue 2`
- `StopException` существует, но она ловится уже на этапе compile/send и не является единственным способом остановить отправку

---

## SMS-события

```php
use Bitrix\Main\Mail\Internal\EventTypeTable;

CEventType::Add([
    'EVENT_NAME' => 'MY_SMS_STATUS',
    'LID' => 'ru',
    'NAME' => 'SMS: смена статуса',
    'DESCRIPTION' => '#PHONE#, #ORDER_ID#',
    'EVENT_TYPE' => EventTypeTable::TYPE_SMS,
]);
```

Дальше создаётся обычный `CEventMessage`, а отправка идёт через тот же `Event::send(...)`.

Но это только слой event-type/event-message. Если вопрос про:

- выбор SMS-провайдера;
- sender ID и from list;
- лимиты и ограничения;
- status callback / result URL;
- REST-методы по сообщениям;

то реальная точка входа уже `messageservice`, а не только `main/mail`.

---

## Очередь и история

```php
use Bitrix\Main\Mail\Internal\EventTable;

$result = EventTable::getList([
    'filter' => ['=SUCCESS' => 'N'],
    'order' => ['DATE_INSERT' => 'ASC'],
    'limit' => 50,
]);

while ($row = $result->fetch())
{
    // $row['EVENT_NAME'], $row['DATE_INSERT'], $row['C_FIELDS']
}
```

---

## Gotchas

- В `CEventType::Add()` поле `LID` — это язык (`ru`, `en`), а в `CEventMessage::Add()` `LID` — это массив `SITE_ID`.
- `Event::send()` возвращает `AddResult`, а `CEvent::Send()` — ID очереди или `false`.
- `Event::sendImmediate()` возвращает строковый статус, а не bool.
- `OnBeforeEventSend` в текущем core реально может отменить шаблон через `return false`; не пиши в reference обратное.
- Если шаблон не найден, `sendImmediate()` вернёт `'0'`, а не `false`.
- `CEvent::Send()` только кладёт событие в очередь. Письмо уйдёт, когда отработает mail-event manager/агент.

---

## Source: `subscribe.md`

# Bitrix Subscribe — справочник

> Reference для Bitrix-скилла. Загружай когда задача связана с рубриками рассылок, подписками, posting-рассылками и auto-template workflow модуля `subscribe`.
>
> Audit note: проверено по текущему core `subscribe/classes/general/*`, `subscribe/install/components/*`. Для shop-core различий между legacy `subscribe.*`, modern `sender.subscribe` и `catalog.product.subscribe*` дополнительно открывай `shop-marketing-analytics.md`.

## Содержание
- Архитектура модуля `subscribe`
- `CRubric`
- `CSubscription`
- Подтверждение / отписка
- `CPosting`
- `CPostingTemplate`
- Gotchas

---

## Архитектура модуля `subscribe`

В текущем core подтверждены следующие основные классы:

```text
CRubric
  └── рубрика / список рассылки

CSubscription
  └── подписка: email, user_id, confirmed, active, набор RUB_ID

CPosting
  └── конкретная рассылка / письмо / очередь отправки

CPostingTemplate
  └── файловые шаблоны для auto-рубрик
```

Не подтверждены как core-API этого модуля:

- `CSender`
- `CSubscribe`
- `CSending`

Не опирайся на них в reference для текущего ядра.

---

## `CRubric`

`CRubric` управляет рубриками рассылок.

### Получить список рубрик

```php
use Bitrix\Main\Loader;

Loader::includeModule('subscribe');

$rubrics = CRubric::GetList(
    ['SORT' => 'ASC'],
    ['ACTIVE' => 'Y', 'LID' => SITE_ID]
);

while ($rubric = $rubrics->Fetch())
{
    // ID, NAME, CODE, SORT, LID, ACTIVE, DESCRIPTION, AUTO, VISIBLE,
    // LAST_EXECUTED, FROM_FIELD, DAYS_OF_MONTH, DAYS_OF_WEEK, TIMES_OF_DAY, TEMPLATE
}
```

### Получить рубрику по ID

```php
$rubric = CRubric::GetByID($rubricId)->Fetch();
```

### Создать / обновить / удалить рубрику

```php
$rubric = new CRubric();

$rubricId = $rubric->Add([
    'NAME' => 'Новости компании',
    'CODE' => 'company_news',
    'LID' => SITE_ID,
    'ACTIVE' => 'Y',
    'VISIBLE' => 'Y',
    'SORT' => 100,
    'DESCRIPTION' => 'Еженедельная рассылка',
    'FROM_FIELD' => 'noreply@example.com',
    'AUTO' => 'N',
]);

if (!$rubricId)
{
    $error = $rubric->LAST_ERROR;
}

$rubric->Update($rubricId, [
    'NAME' => 'Актуальные новости компании',
]);

CRubric::Delete($rubricId);
```

Если рубрика `ACTIVE=Y` и `AUTO=Y`, ядро может добавить агент `CPostingTemplate::Execute();`.

---

## `CSubscription`

`CSubscription` хранит email-подписки и привязку к рубрикам.

### Получить список подписок

```php
$subscriptions = CSubscription::GetList(
    ['DATE_INSERT' => 'DESC'],
    [
        'ACTIVE' => 'Y',
        'CONFIRMED' => 'Y',
        'RUBRIC_MULTI' => [$rubricId],
    ]
);

while ($subscription = $subscriptions->Fetch())
{
    // ID, USER_ID, EMAIL, FORMAT, CONFIRM_CODE, CONFIRMED, DATE_INSERT, DATE_UPDATE
}
```

### Получить по ID

```php
$subscription = CSubscription::GetByID($subscriptionId)->Fetch();
```

### Получить по email

```php
$subscription = CSubscription::GetByEmail('user@example.com', false)->Fetch();
```

Важная деталь текущего core:

- второй аргумент `GetByEmail($email, $user_id = false)` — это **`USER_ID`**, а не `SITE_ID`

### Получить рубрики подписки

```php
$rubrics = CSubscription::GetRubricList($subscriptionId);
while ($rubric = $rubrics->Fetch())
{
    // ID, NAME, SORT, LID, ACTIVE, VISIBLE
}
```

### Создать подписку

```php
$subscription = new CSubscription();

$subscriptionId = $subscription->Add([
    'USER_ID' => $USER->IsAuthorized() ? (int)$USER->GetID() : false,
    'EMAIL' => 'user@example.com',
    'FORMAT' => 'html',
    'ACTIVE' => 'Y',
    'CONFIRMED' => 'Y',
    'RUB_ID' => [$rubricId],
    'SEND_CONFIRM' => 'N',
], SITE_ID);

if (!$subscriptionId)
{
    $error = $subscription->LAST_ERROR;
}
```

Подтверждённые полезные поля:

- `USER_ID`
- `EMAIL`
- `FORMAT` (`html` / `text`)
- `ACTIVE`
- `CONFIRMED`
- `RUB_ID`
- `SEND_CONFIRM`
- `ALL_SITES`

### Обновить подписку

```php
$subscription = new CSubscription();

$ok = $subscription->Update($subscriptionId, [
    'ACTIVE' => 'Y',
    'CONFIRMED' => 'Y',
    'RUB_ID' => [$rubricId1, $rubricId2],
    'SEND_CONFIRM' => 'N',
], SITE_ID);
```

### Удалить подписку

```php
CSubscription::Delete($subscriptionId);
```

---

## Подтверждение / отписка

При `SEND_CONFIRM <> 'N'` ядро отправляет событие `SUBSCRIBE_CONFIRM` и использует `CONFIRM_CODE`.

Есть подтверждённый helper:

```php
CSubscription::Authorize($subscriptionId, $confirmCode);
```

Также можно подтвердить подписку через `Update()`:

```php
$subscription = new CSubscription();
$subscription->Update($subscriptionId, [
    'CONFIRM_CODE' => $confirmCode,
], SITE_ID);
```

В текущем core не нужно придумывать поле `CODE` или endpoint `unsubscribe.php` как базовый контракт модуля. Legacy subscribe-flow работает через `ID` + `CONFIRM_CODE` и компонент `subscribe.edit`.

---

## `CPosting`

`CPosting` — это конкретная рассылка.

### Создать posting

```php
$posting = new CPosting();

$postingId = $posting->Add([
    'FROM_FIELD' => 'noreply@example.com',
    'TO_FIELD' => 'noreply@example.com',
    'SUBJECT' => 'Новости недели',
    'BODY_TYPE' => 'html',
    'BODY' => '<p>Контент письма</p>',
    'DIRECT_SEND' => 'N',
    'SUBSCR_FORMAT' => 'html',
    'RUB_ID' => [$rubricId],
    'GROUP_ID' => [],
]);

if (!$postingId)
{
    $error = $posting->LAST_ERROR;
}
```

Ключевые поля, подтверждённые по текущему core/admin UI:

- `FROM_FIELD`
- `TO_FIELD`
- `SUBJECT`
- `BODY_TYPE`
- `BODY`
- `DIRECT_SEND`
- `SUBSCR_FORMAT`
- `RUB_ID`
- `GROUP_ID`
- `EMAIL_FILTER`
- `AUTO_SEND_TIME`

### Получить posting

```php
$posting = CPosting::GetByID($postingId)->Fetch();
```

### Получить список posting

```php
$postingApi = new CPosting();

$list = $postingApi->GetList(
    ['ID' => 'DESC'],
    ['STATUS_ID' => 'D'],
    ['ID', 'STATUS', 'FROM_FIELD', 'TO_FIELD', 'SUBJECT', 'DATE_SENT'],
    false
);

while ($row = $list->Fetch())
{
    // ...
}
```

### Обновить / удалить

```php
$posting = new CPosting();

$posting->Update($postingId, [
    'SUBJECT' => 'Новая тема письма',
]);

CPosting::Delete($postingId);
```

---

## Запуск отправки posting

Для боевой отправки posting обычно переводят из draft в processing:

```php
$posting = new CPosting();

$posting->ChangeStatus($postingId, 'P');
```

Что делает current core:

- собирает `b_posting_email`
- набирает получателей из рубрик / групп / BCC
- дальше `CPosting::AutoSend(...)` или cron/agent доотправляет батчами

Для ручного запуска:

```php
CPosting::AutoSend($postingId, true, SITE_ID);
```

Для тестовой или синхронной отправки есть:

```php
$posting = new CPosting();
$result = $posting->SendMessage($postingId, 0, 0, false);
```

Но `SendMessage()` блокирует выполнение и не подходит как default-стратегия для массовой рассылки.

---

## `CPostingTemplate`

`CPostingTemplate` в текущем core работает не как DB-шаблон письма, а как файловый auto-template.

Шаблоны лежат в:

```text
getLocalPath('php_interface/subscribe/templates', BX_PERSONAL_ROOT)
```

### Получить список шаблонов

```php
$templates = CPostingTemplate::GetList();
// массив путей, а не DB result
```

### Получить шаблон по пути

```php
$paths = CPostingTemplate::GetList();
$template = CPostingTemplate::GetByID($paths[0] ?? '');
```

### Auto-run

Если рубрика настроена как `AUTO=Y`, агент вызывает:

```php
CPostingTemplate::Execute();
```

Он рассчитывает расписание рубрики, генерирует posting через шаблон и переводит его в отправку.

---

## Gotchas

- В текущем core модуля `subscribe` нет подтверждённого API `CSender`, `CSubscribe`, `CSending`. Не описывай их как штатный контракт этого ядра.
- `CSubscription::GetByEmail($email, $userId)` вторым параметром принимает `USER_ID`, а не `SITE_ID`.
- `CSubscription::GetRubricList($subscriptionId)` принимает именно ID подписки и возвращает строки рубрик с полями `ID/NAME/...`, а не `RUBRIC_ID`.
- Для `CPosting::Add()` используй `RUB_ID`, а не `RUBRIC_ID`.
- `CPostingTemplate::GetList()` возвращает массив путей, не `CDBResult`.
- `CPosting::ChangeStatus($id, 'P')` — нормальная точка входа в очередь отправки. Не выдумывай отдельную сущность “sending job”.
- `SendMessage()` синхронен. Для боевой рассылки ориентируйся на queue/agent/cron workflow.
- Если включаешь `SEND_CONFIRM`, не забывай, что подписка останется неподтверждённой до прохождения confirm-flow.

---
