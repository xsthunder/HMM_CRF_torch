## env setup

[Using Anaconda behind a company proxy — Anaconda documentation](https://docs.anaconda.com/anaconda/user-guide/tasks/proxy/)

### gpu

### cpu

```bash
# for windows
conda create -n py3torch-cpu --file package-list-cpu.txt -c pytorch
pip install mock==4.0.1 sure==1.4.11
```

or
 
```bash
conda create -n py3torch-cpu python=3.7 scipy=1.4.1 -y
# py3.7 for asyncio.WindowsProactorEventLoopPolicy() support
conda activate py3torch-cpu
conda install pytorch=1.4.0 torchvision=0.5.0 cpuonly=1.0 ipykernel=5.1.4 -c pytorch -y
# for test
pip install sure --yes
```

### export notebook

`notebook2script.py` from [course-v3/nbs/dl2 at master · fastai/course-v3](https://github.com/fastai/course-v3/tree/master/nbs/dl2)