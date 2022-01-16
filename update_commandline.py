

_item = {}

def update_commandline(current, total):
    _printProgressBar(current, total)

def initialize(total, start=0):
    if total > 0:
        _item['incrementer'] = Incrementer(total, start)
    else:
        import logging
        logging.getLogger(__name__).info('No incrementor for 0 total')

def increment():
    if _item['incrementer']:
        _item['incrementer'].increment()

class Incrementer:
    def __init__(self, total, start=0) -> None:
        self.total = total
        self.current = start
        self.print()
    
    def increment(self):
        if self.current == None or self.total == None:
            raise Exception('Initalize before incrementing')
        self.current = self.current +1
        update_commandline(self.current, self.total)

    def print(self):
        if self.current == None or self.total == None:
            raise Exception('Initalize before incrementing')
        if self.total > 0:
            update_commandline(self.current, self.total)

    def __str__(self) -> str:
        return f'current: {self.current}, total: {self.total}'




# Credit to https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
# Print iterations progress
def _printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

if __name__ == '__main__':
    import time
    for n in range(100):
        _printProgressBar(n, 100)
        time.sleep(0.5)
