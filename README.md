# async-batcher
Small package that provides a way to add zero latency cost dynamic batching for ML model serving on web frameworks.

---
## Usage
### Installing
Clone the project and just run:
```
make install
```

### Create you own model
Simply create an instance of the Batcher class and start it.
After that you can simply request a prediction with the `predict` function.
```python
from async_batcher import Batcher

batcher = Batcher(
	batch_prediction_fn=lambda x : x, 
	event_loop=event_loop,
	max_batch_size=max_batch_size
)

batcher.start()

batcher.predict(x)
``` 

Alternatively, if the event loop is initialized later, you can pass it to the Batcher instance when you start it. For example in FastAPI you can do the following:

```python
@app.on_event("startup")
async def startup_event():
	loop = asyncio.get_running_loop()
	asyncio.create_task(batcher.start(loop))
```

For a hackable example you can check the `fastapi_example.py` module from the example directory.
