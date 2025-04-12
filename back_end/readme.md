

1.  启动redis

   ```bash
   redis-server
   ```

   

2.  运行 main 文件

   ```bash
   python main.py
   ```

   

3. 启动celery

   ```bash
   celery -A celery_task.celeryapp  worker --loglevel=info  -P threads
   ```

   