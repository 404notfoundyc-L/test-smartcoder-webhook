from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
import traceback

from e2b_code_interpreter import CodeInterpreter
from util.sse_util import format_sse

class BoundedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None, queue_size=0, *args, **kwargs):
        self._work = Queue(maxsize=queue_size)
        super().__init__(max_workers, *args, **kwargs)

class CodeExecutionService:
 def __init__(self, logger, max_workers=5, queue_size=10):
       .logger = logger
        self.output_queue = Queue()
        self.executor = BoundedThreadPoolExecutor(max=max_workers, queue_size=queue_size)

    def handle_stderr(self, stderr):
        self.logger.info(f"data: [Code Interpreter stderr] {stderr}")
        self.output_queue.put(format_sse(stderr))

    def handle_stdout(self, stdout):
        self.logger.info(f"data: [Code Interpreter stdout] {stdout}")
        self.output_queue.put(format_sse(stdout))

    def handle_result(self, result):
        self.logger.info(f"data: [Code Interpreter result] {result}")
        # self.output_queue.put(format_sse(result))

    def execute(self, code: str, language: str):
        try:
            with CodeInterpreter() as sandbox:
 kernel_id = sandbox.notebook.create_kernel(kernel_name=language.lower())
                exec_result = sandbox.notebook.exec_cell(
                    code,
                    kernel_id,
                    on_stderr=self.handle_stderr,
                    on_stdout=self.handle_stdout,
                    on_result=self.handle_result,
                    timeout=60
                )

                if exec_result.error:
                    self.logger.info(f"[Code Interpreter error] {exec_result.error}")
                    for errorValue in exec_result.error.traceback_raw:
                        self.output_queue.put(format_sse(errorValue))
                        self.logger.info(errorValue)

       .error(f"TimeoutError during code execution: {str(e)}")
            self.logger.error("Traceback:\n" + traceback.format self.output_queue.put(format_sse(traceback.format_exc()))
        except Exception as e:
            self.logger.error(f"Exception during code execution: {str(e)}")
            self.logger.error("Traceback:\n" + traceback.format_exc())
            self.output_queue.put(format_sse(traceback.format_exc()))
        finally:
            self.output_queue.put(None)  # Sentinel value to indicate the end of processing

    def generate(self, code, language):
        self.output_queue.put(format_sse("```"))
        #线程池提交任务
        try:
            self.executor.submit(self.execute, code, language)
        except Exception as e:
            self.logger.error(f"Failed to submit task: {str(e)}")
            self.output_queue.put(format_sse(str(e)))
        while True:
            output = self.output_queue.get()
            if output is None:
                yield format_sse("```")
                break  # Sentinel value received, end the generator
            self.logger.debug(output)
            yield output

    def shutdown(self):
        self.executor.shutdown(wait=True)

# 示例使用
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
   ExecutionService(logger, max_workers=5, queue_size=10)

    # 示例调用 generate 方法
    for output in service.generate("print('Hello, World!')", "python"):
        print(output)

    # 关闭线程池
    service.shutdown()

    print("finish1")
