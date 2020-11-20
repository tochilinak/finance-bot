# Что сейчас в bot_example.py (20.11.2020 19:00)

фунции для хэндлеров (не для conversation):  
* `start_reaction` реагирует на /start сообщением "lol))". В context есть атрибут bot, в котором метод send_message, однако можно его можно заменить на text_reply из атрибута message update'a  
* `reverse_reaction` реагирует на /reverse, отправляя развернутую последующую часть сообщения. Тут отправил сообщение через bot, получилось длиннее  
* `ri_reaction` реагирует на /ri, отправляет значение переменной, которая каждые 10 секунд меняет значение на случайное (она общая для всех чатов)


Создан updater, из него взят dispatcher, туда добавлены 3 CommandHandler'a на основе тех функций  
Добавлена задача по обновлению значения, которое выдаётся по /ri. При этом, это значение хранится как раз внутри задачи  
Кроме того, есть совсем простой диалог:  
Входная точка в него - команда /start_conv, после чего бот просить указать действие и возвращает SELECT_ACTION, которому 
соответсвует хэндлер, обрабатывающий его и дальше либо просящий новую команду, либо идущий к названию компании (которые он 
обработать не может)  
  
Потом бот запускается