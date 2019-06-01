# Pavillion
Pavilion algorithm for handling asynchronous arrival/departure of workers in the waiting and active queue
# Introduction
Pavilion tries to retain workers in the active queue -- a queue which contains workers who are engaged with the task-- in addition to waiting queue based on turnover conditions, e.g. when workers leave the task either from the waiting or active queue. A worker can leave the task either when she submits a task, returns it, or abandons it.
