import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple
import concurrent.futures
from asyncio import (
	AbstractEventLoop, 
	Queue, 
	wait_for, 
	TimeoutError as AsyncTimeoutError
)

log = logging.getLogger(__name__)


class Batcher:
	def __init__(
		self, 
		batch_prediction_fn: Callable[[List[Any]], List[Any]], 
		event_loop: Optional[AbstractEventLoop] = None, 
		max_batch_size: int = 1,
		max_queue_size: int = 100
	) -> None:
		self.batch_prediction_fn = batch_prediction_fn
		self.event_loop = event_loop
		self.max_batch_size = max_batch_size
		self.wait_time = 5
		
		self.queue = Queue(maxsize=max_queue_size)


	async def predict(self, input_context: Any) -> Awaitable[Any]:
		job_future = self.event_loop.create_future()
		await self.queue.put((job_future, input_context))

		return await job_future


	def process_batch(self, batch: List[Tuple[Awaitable[Any], Any]]) -> None:
		try:
			jobs_future, input_contexts = zip(*batch)

			predictions = self.batch_prediction_fn(input_contexts)

			for idx, prediction in enumerate(predictions):
				jobs_future[idx].set_result(prediction)
		except Exception as e:
			log.exception(f"Error processing batch: {e}")

			for job_future in jobs_future:
				job_future.set_exception(e)

		finally:
			for job_future in jobs_future:
				self.queue.task_done()


	async def start(self, event_loop: Optional[AbstractEventLoop] = None):
		if self.event_loop is None:
			if event_loop is None:
				raise ValueError("The event loop was not initialized.")

			log.info("Setting the event loop.")
			self.event_loop = event_loop


		with concurrent.futures.ThreadPoolExecutor(1) as pool:
			while True:
				log.debug("Starting a batch processing")
				current_batch: List[Tuple[Awaitable[Any], Any]] = [await self.queue.get()]

				while (
					len(current_batch) < self.max_batch_size 
					and not self.queue.empty() 
				):
					try:
						current_batch.append(await wait_for(
							self.queue.get(), self.wait_time
						))
					except AsyncTimeoutError:
						break
					
				log.debug(f"Processing batch of size {len(current_batch)}")
				await self.event_loop.run_in_executor(pool, self.process_batch, current_batch)

