## env setup

[Using Anaconda behind a company proxy — Anaconda documentation](https://docs.anaconda.com/anaconda/user-guide/tasks/proxy/)

### gpu

### cpu

`conda create -n py3torch-cpu --file package-list-cpu.txt`

or
 
```
conda create -n py3torch-cpu python=3.7 scipy -y
# py3.7 for asyncio.WindowsProactorEventLoopPolicy() support
conda activate py3torch-cpu
conda install pytorch torchvision cpuonly -c pytorch -y
# for test
pip install sure
```

### export notebook

`notebook2script.py` from [course-v3/nbs/dl2 at master · fastai/course-v3](https://github.com/fastai/course-v3/tree/master/nbs/dl2)