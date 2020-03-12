# py3.7 for asyncio.WindowsProactorEventLoopPolicy() support
conda create -n py3torch python=3.7 scipy=1.4.1 pandas=1.0 tqdm=4.42 -y

conda activate py3torch
# cpu
# conda install pytorch=1.4.0 torchvision=0.5.0 cpuonly=1.0 ipykernel=5.1.4 -c pytorch -y
# gpu
conda install pytorch=1.4.0 torchvision=0.5.0 cudatoolkit=10.1 ipykernel=5.1.4 -c pytorch -y

# for test
# avoid tensorflow
yes | pip install seqeval[cpu] --no-deps
yes | pip install sure
# tqdm jupyter support
conda install -c conda-forge ipywidgets -y
conda install pytorch torchvision cudatoolkit=10.1 -c pytorch -y 