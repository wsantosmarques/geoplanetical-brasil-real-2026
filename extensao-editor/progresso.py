"""Espelha o registro da instalação em eventos de interface, sem acessar Tk no worker."""
class ProgressLog:
    def __init__(self, file, notify):
        self.file, self.notify, self.pending = file, notify, ''
    def write(self, text):
        count = self.file.write(text)
        self.file.flush()
        self.pending += text
        while '\n' in self.pending:
            line, self.pending = self.pending.split('\n', 1)
            if line.strip() and not line.lstrip().startswith('{'): self.notify(line.strip())
        return count
    def flush(self):
        self.file.flush()
