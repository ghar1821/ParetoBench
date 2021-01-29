# Dataset

This folder contains the dataset used in the manuscript.

Levine\_13dim and Samusik\_01 datasets are each contained within 1 csv file. However, the other 2 datasets have to be split into multiple csv files for github to accept it without having to use git lfs which imposes limit on storage space and bandwidth (**they are not entirely free!**).

For Levine\_32dim and Samusik\_all dataset, the data has been split into multiple chunks. Only the very first part (*part1.csv*) contains the csv file header. The remaining chunks do not!

To merge the files into 1 csv file (for each dataset!), simply use command line (terminal on mac):
1. Use ``cd`` to change to the directory where the csv files are stored
2. Run ``cat *.csv > Levine_32dim.csv`` for Levine\_32dim or ``cat *.csv > Samusik_all.csv`` for Samusik\_all dataset.

Voila! you should now have the merged csv file!