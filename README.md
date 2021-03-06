## NOTE
Due to large jar size runner.jar not presented here.
In order to start you need clone https://github.com/NikitaMishin/SemiLocalLcs/ and build jar file with all dependencies and place it to this project with name runner.jar

## Overview
  <p>The Comment Clone Detector "JavaCloneD" finds and visualizes clones that contain in Javadoc comments.
        The tool finds exact and fuzzy clones. Clones split onto the groups and each group forms an acyclic-oriented
        graph.
        The relation between nodes (edge) may be interpreted as follows:
        for each node that has children (i.e ancestors) edge shows that associated with that node Javadoc comment was
        partially copy-pasted and may be edited from children.</p>
        <p>
        Further, each such group may be displayed as a naturally oriented graph and for each node in the graph we can
        build derivation tree.</p>

## Requirements
For launch **JavaCloneD** you need to install docker and have browser.
Note you need to build jar file from semiLocalLCS repo and place in JavaCloneD repo as runner.jar

## Launch
1) <code> git clone https://github.com/NikitaMishin/JavaCloneD </code> 
2) <code> cd JavaCloneD/ </code>
3) <code> docker build -t  javacloned:latest . </code>
4) <code> docker run -it -p 5000:5000 javacloned:latest </code> here first 5000 port on docker machine and second one container port 
5) visit <code> http://127.0.0.1:5000/home </code>

If you don't want to clone repo you can get latest image from dockerhub
 1) <code> docker pull murmulla/javacloned </code>
 2) previous steps 4 and 5
