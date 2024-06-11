# Space Treasure RL Task

Author: Paul A. Bloom

Date: Jan 2 2019

### A gamified 2-stage reinforcement learning task built in Python

Task design based on [Daw et al., 2011](https://www.ncbi.nlm.nih.gov/pubmed/21435563) and [Decker et al., 2016](https://www.ncbi.nlm.nih.gov/pubmed/27084852). While virtually all task contingencies are identical to previous versions of the task, we make several modifications here to run this task with 6-13 year-old children:

*	The transition matrix is explicitly spatial, and all on one screen (i.e. participants can always see both portals and planets)
*	Trials are faster (usually under 3s), such that most participants complete the task (200 trials) in roughly 10 minutes
*	We have added animations, sounds, and music in attempts to 'gamify' the task and engage children for the task duration

<p float="left">
  <img src="/images/instructions/Slide01.jpg" width="300" />
  <img src="/images/demoImg.png" width="300" /> 
</p>

### To run the game: 

`python main.py` from command line

### Python Dependencies:

pygame
numpy 
pandas
random
datetime
os
textwrap
