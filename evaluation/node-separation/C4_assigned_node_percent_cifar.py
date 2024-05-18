import sys

sys.path.append('../modules/')
from node_separation_dropout import NodeSepDropoutLayer
from cnn_model_gt import Net as Net_T
from model_wrapper_gt import NetWrapper_T
from import_data import load_cifar
from misc import write_to_json
from torch import nn, optim
from os.path import exists
import torchvision.transforms as transforms
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def main():
  batch_size = 128
  epochs = 12
  classes = ['plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
  transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
  _, _, _, trainloader, validationloader, testloader = load_cifar(batch_size, transform)
  selected = (0,)
  mode = 'probability'
  percent_nodes_for_targets = [0.01, 0.03, 0.05, 0.1, 0.2]
  node_sep_probability = 0.0001
  start_attack = 0
  num_to_assign = None
  for i in range(1, 6):
    for perc in percent_nodes_for_targets:
      if not exists(f'../output/evaluation/node-separation/C4-assigned-node-percent-cifar-p{perc}-{i}.json'):
        print('.....................New Model Running.....................')
        dropout = NodeSepDropoutLayer(0.5, mode, perc, node_sep_probability, num_to_assign)
        net = Net_T(dropout)
        netwrapper = NetWrapper_T(net, nn.CrossEntropyLoss(), optim.Adam, [1e-3])
        netwrapper.fit(trainloader, validationloader, selected, epochs, False, start_attack)
        accuracy, _, conf_matrix, per_class_acc, per_class_precision = netwrapper.evaluate(testloader)
        write_to_json(f'evaluation/node-separation/C4-assigned-node-percent-cifar-p{perc}-{i}', 'model', netwrapper, accuracy, conf_matrix, per_class_acc, per_class_precision, classes)
      else:
        print(f'file found')


if __name__ == "__main__":
  main()