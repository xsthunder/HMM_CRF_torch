set -e

# download data

## for data/CRF/ResumeNER

p='../data/CRF/ResumeNER'

for file in $(cat $p/data-source-list.txt)
do
	wget $file -P $p
done

## for data/HMM
wget https://raw.githubusercontent.com/xsthunder/jieba/master/jieba/dict.txt -P ../data/HMM


# set up conda env
# https://docs.travis-ci.com/user/environment-variables/#default-environment-variables
# TRAVIS=TRUE
if test $TRAVIS
then
    source $HOME/miniconda/etc/profile.d/conda.sh
    conda activate py3torch-cpu
fi


# run test
for file in ./*.py
do
	python $file
done
