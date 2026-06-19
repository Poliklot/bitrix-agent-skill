# Eval-набор бытовых Bitrix-запросов

Используй при доработке compact-версии. Оцени: правильный route, нет плохого первого шага, есть полезный Bitrix-native ответ по `answer-contracts.md`. Если ответ должен показать “где проверить в проекте”, grep-команды бери из `core-grep-cookbook.md`.

| ID | Prompt | Expected route | Must not start with |
|---|---|---|---|
| B001 | Как в PHP поставить meta title в Битриксе? | `developer-primitives`, `first-answer-pitfalls`, `developer-cards`, `components-admin-ui`, `search-seo-ops` | ручной `<meta name="title">` |
| B002 | Где менять meta description? | primitives/cards + search/seo | meta руками в каждом файле |
| B003 | Как добавить canonical на детальной? | cards + search/seo + commerce if confirmed | правка ядра component |
| B004 | Как подключить CSS? | Asset/cards/components-admin-ui | echo `<link>` |
| B005 | Как подключить JS в компоненте? | Asset/cards/components-admin-ui | random inline script |
| B006 | Как добавить OG meta? | AddHeadString/Asset/search-seo | echo в body |
| B007 | Как сделать редактируемый текст? | IncludeFile/cards | hardcode text |
| B008 | Как вывести включаемую область? | IncludeFile/cards | custom mini-CMS |
| B009 | Как добавить хлебную крошку? | AddChainItem/cards | manual breadcrumbs HTML |
| B010 | Почему крошки дублируются? | cards/components | clear all cache first |
| B011 | Как получить текущего пользователя? | `$USER`/users-security | `$_SESSION` |
| B012 | Показать блок авторизованным | `$USER`, cache caveat | personalized cached HTML |
| B013 | Как получить GET-параметр? | Context request | raw `$_REQUEST` |
| B014 | Как обработать POST? | request + sessid/security | no CSRF |
| B015 | Добавить параметр к URL | `GetCurPageParam` | concat `REQUEST_URI` |
| B016 | Подключить iblock | `Loader::includeModule` | call API before include |
| B017 | Проверить sale | module dir + Loader | assume sale exists |
| B018 | Сделать 404 | `CHTTP::SetStatus`, `ERROR_404`, `404.php` | echo 404 |
| B019 | 404 отдаёт 200 | status/routing/component | redirect home first |
| B020 | Redirect after form | `LocalRedirect`, no output | JS redirect first |
| B021 | Вывести картинку элемента | `CFile::GetPath/ResizeImageGet` | hardcode `/upload` |
| B022 | Сделать превью | `ResizeImageGet` | HTML width/height only |
| B023 | Вывести свойство инфоблока | component params/arResult/API | SQL property table |
| B024 | PROPERTY пустой | params/cache/result_modifier | assume property exists |
| B025 | Изменения не видны | component/managed/composite cache | disable all cache |
| B026 | Кешировать компонент | cache keys, `StartResultCache` | cache user-specific data |
| B027 | Чужие данные в кеше | personalization/composite/groups | clear cache only |
| B028 | Отправить письмо | mail events/templates | PHP `mail()` first |
| B029 | Форма не шлёт письмо | event/template/SITE_ID/agents | “SMTP сломан” first |
| B030 | AJAX в компоненте | project ajax/controller + sessid | endpoint without sessid |
| B031 | Обработчик события | EventManager/local module | code in template |
| B032 | Где писать класс | local module/project namespace | edit core classes |
| B033 | Добавить агента | CAgent/project scheduler | random cron only |
| B034 | Очистить кеш инфоблока | tagged/managed cache | delete all cache first |
| B035 | Путь к ресурсу шаблона | `$this->GetFolder()` | unverified `GetTemplatePath` |
| B036 | Пагинация списка | PageNavigation/NavStart | raw LIMIT only |
| B037 | Вторая страница пустая | filter/count/sort/nav/cache | page size tweak only |
| B038 | Добавить lang-фразу | `Loc::getMessage` | hardcode reusable string |
| B039 | Пользовательское поле | UF API/migration | manual DB change |
| B040 | HL-блок справочник | highloadblock API/migration | raw table only |
| B041 | Обновить цену | catalog API after module check | SQL price update |
| B042 | Статус заказа | sale API after module check | SQL order update |
| B043 | Обмен 1С | checkauth/init/file/import/logs | “just upload XML” |
| B044 | Товар есть в админке, нет на сайте | visibility chain + catalog/1C refs | clear cache only |
| B045 | REST webhook | scopes/auth/permissions | token in public template |

Gate: перед релизом бытового слоя выбрать минимум 15 prompt из разных доменов; `fail = 0`. Полный checklist — `release-gate.md`.
