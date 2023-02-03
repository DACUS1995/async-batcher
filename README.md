# async-batcher
Small package that provides zero latency cost dynamic batching for ML model serving for async endpoints handlers.

---
## Usage
### Installing
Clone the project and just run:
```
make install
```

### Create you own model
Simply create an instance of the Batcher and start the it.
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

Alternatively if the event loop is initialized later you can pass it when you start the batcher. For example in FastAPI you can do the following:

```python
@app.on_event("startup")
async def startup_event():
	loop = asyncio.get_running_loop()
	asyncio.create_task(batcher.start(loop))
```

For a hackable example you can check the `fastapi_example.py` module from the example directory.
