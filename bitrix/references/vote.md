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
