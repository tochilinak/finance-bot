# Какие бывают хэндлеры

* `CommandHandler` - регирует на команды по типу /start  
* `MessageHandler` - реагирует на сообщения. можно добавить фильтры, например, проверку на то, что сообщение не команда  
* `ConversationHandler` - нужен для длиной беседы. Состоит из хэндлеров, которые бывают входными, выходными или ни теми, не другими.
Выходные возвращают `ConversationHandler.END`, остальные - ключ, по которому понятно, в один из какоих хэндлеров "идти" дальше. 
Сам хэндлер задаётся входными, словарём _ключ - список хэндлеров_, запасными хэндлерами, которые срабатывают, если не сработали остальные хэндлеры