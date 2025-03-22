from torch.utils.data import Dataset, DataLoader

class ChessDataset(Dataset):

    def __init__(self, data_dir, transform=None):
        self.data = data_dir

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]
