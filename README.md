# timekeeper
Basic time tracking cli for projects and roles. Time entries stored in readable json format. 

```console
$ python3 ./main.py --help
usage: main.py [-h] {init,toggle,sum} ...

Time tracking utility.

positional arguments:
  {init,toggle,sum}
    init             Initialize a new project.
    toggle           Toggle time tracking for a project.
    sum              Summarize time spent on projects.

options:
  -h, --help         show this help message and exit
```

# why
I needed a quick and dirty time tracker for a project and I didn't want to set up
some app with an account so I asked chatGPT to write a script that performed the
things I needed, that turned into version [`0.1.0`](https://github.com/dbellotti/timekeeper/releases/tag/v0.1.0).

Since then, I have been using this repo to demo and practice various engineering
curiosities and skills. Version `0.2.0` demonstrates a move from imperative,
scripted, ai generated solution to a clean architecture repo. I was surprised to
discover just how much more code was required when I applied more and more OOP to
the codebase, but I am pleased with the understandability and expandability that
has resulted.
