#!/usr/bin/env bash
set -e


sudo yum groupinstall -y "Development Tools"
sudo yum install -y zlib-devel
sudo yum install -y ncurses-devel

rm -rf ~/bld
mkdir ~/bld


cd ~/bld
wget https://downloads.sourceforge.net/project/samtools/samtools/1.3.1/samtools-1.3.1.tar.bz2
bunzip2 samtools-1.3.1.tar.bz2
tar -xvf samtools-1.3.1.tar
cd samtools-1.3.1
make
sudo make install

cd ~/bld
wget https://sourceforge.net/projects/samtools/files/samtools/1.3.2/htslib-1.3.2.tar.bz2
bunzip2 htslib-1.3.2.tar.bz2
tar -xvf htslib-1.3.2.tar
cd htslib-1.3.2
make
sudo make install

cd ~/bld
wget https://github.com/arq5x/bedtools2/releases/download/v2.26.0/bedtools-2.26.0.tar.gz
tar -zxvf bedtools-2.26.0.tar.gz
cd bedtools2
make
sudo make install

cd ~/bld

exit


