import unittest
import asyncio
from unittest.mock import MagicMock

from async_batcher import Batcher

class TestBatcher(unittest.IsolatedAsyncioTestCase):

	async def asyncSetUp(self):
		self.loop = asyncio.new_event_loop()
		asyncio.set_event_loop(None)

		self.batch_prediction_fn = MagicMock(return_value=[1, 2, 3])
		self.batcher = Batcher(batch_prediction_fn=self.batch_prediction_fn, max_batch_size=3, max_queue_size=100)


	async def asyncTearDown(self):
		self.loop.close()
		await asyncio.sleep(0)


	async def test_predict(self):
		result = await self.batcher.predict(1)
		self.assertEqual(result, 1)


	async def test_process_batch(self):
		job_future1 = self.loop.create_future()
		job_future2 = self.loop.create_future()
		job_future3 = self.loop.create_future()

		batch = [(job_future1, 1), (job_future2, 2), (job_future3, 3)]
		self.batcher.process_batch(batch)
		
		self.assertEqual(job_future1.result(), 1)
		self.assertEqual(job_future2.result(), 2)
		self.assertEqual(job_future3.result(), 3)
		self.batch_prediction_fn.assert_called_once_with([1, 2, 3])


	async def test_start(self):
		async def run_until_complete():
			await self.batcher.start(self.loop)
	
		task = asyncio.ensure_future(run_until_complete(), loop=self.loop)
		await asyncio.sleep(0)
	
		job_future1 = self.loop.create_future()
		job_future2 = self.loop.create_future()
		job_future3 = self.loop.create_future()
		self.batcher.predict(1)
		self.batcher.predict(2)
		self.batcher.predict(3)
	
		await asyncio.sleep(0)
		self.assertEqual(job_future1.result(), 1)
		self.assertEqual(job_future2.result(), 2)
		self.assertEqual(job_future3.result(), 3)
		self.batch_prediction_fn.assert_called_once_with([1, 2, 3])
	
		task.cancel()
		with self.assertRaises(asyncio.CancelledError):
			await task


if __name__ == "__main__":
	unittest.main()
