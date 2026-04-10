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
