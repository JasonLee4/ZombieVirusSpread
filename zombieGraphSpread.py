# -*- coding: utf-8 -*-
"""Copy of Copy_of_Copy_of_StartingCode.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mhq6X1DO3_-nQdeSGvAHVMfdmWr5jHwR
"""

import math
import time
import numpy as np
import scipy.linalg as lin
import scipy.sparse as sp
import scipy.sparse.linalg as splin
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from PIL import Image

def draw_with_image(G, pos, imgloc, zombie_imgloc, human_imgloc):
    zimg = mpimg.imread(zombie_imgloc)
    himg = mpimg.imread(human_imgloc)

    fig = plt.figure(1, figsize=(10,10))
    ax=plt.subplot(111)
    ax.set_aspect('equal')
    nx.draw_networkx_edges(G,pos,ax=ax)

    plt.xlim(-1,1)
    plt.ylim(-1,1)

    trans=ax.transData.transform
    trans2=fig.transFigure.inverted().transform

    piesize=0.04 # this is the image size
    p2=piesize/2.0
    for n in G:
        xx,yy=trans(pos[n]) # figure coordinates
        xa,ya=trans2((xx,yy)) # axes coordinates
        a = plt.axes([xa-p2,ya-p2, piesize, piesize])
        a.set_aspect('equal')
        if G.nodes[n]['zombie']:
            a.imshow(zimg)
        else:
            a.imshow(himg)
        a.axis('off')
    ax.axis('off')
    if imgloc:
        plt.savefig(imgloc+'.png')
        plt.close()
        return imgloc+'.png'
    else:
        plt.show()

def draw_with_color(G, pos, imgloc):
    """
    FUNCTION draw_with_color
        draw graph, with nodes colored according to the Color Changing Rule
    ARGUMENTS
        G:      networkx graph      city to draw
        pos:    networkx position   positions of city to draw
        imgloc: string or None      location to save; if None, then do not save.
    """
    node_col = ['midnightblue' if not G.nodes[node]['zombie'] == 1  else 'seagreen' for node in G.nodes()]
    plt.figure(1,figsize=(10,10))
    nx.draw(G,
        vmin=0,
        vmax=1,
        node_color = node_col, #[G.nodes[i]['zombie'] for i in G],
        node_sizes = [30] * len(G),
        pos=pos)
    ax = plt.gca()
    ax.set_axis_off()
    if imgloc:
        plt.savefig(imgloc+'.png')
        plt.close()
        return imgloc+'.png'
    else:
        plt.show()

def draw_and_save(G, pos, loc, imglist, save_images, show_images):
    """
    FUNCTION draw_and_save
        draw graph and then save/show, depending on options
    ARGUMENTS
        G:           networkx graph     city to draw / save
        pos:         networkx position  positions of city to draw
        loc:         string or None     location to save; if None, then do not save
        imglist:     list of strings    list of image locations, already saved
        save_images: bool               if True, then save image to loc
        show_images: bool               if True, then display image as output
    MODIFIES
        imglist: if image is saved, append loc to imglist
    """
    if save_images:
        imglist.append(draw_with_image(G,pos,loc, "zombie.png", "human.png"))
    if show_images:
        draw_with_image(G,pos,None, "zombie.png", "human.png")

def animate(imglist, saveloc):
    """
    FUNCTION animate
        create gif from images
    ARGUMENTS
        imglist: list of strings  image locations, to compress into gif
        saveloc: string           location to save gif
    """
    print('saving animation to '+saveloc+'/zombies.gif')
    img, *imgs = [Image.open(f) for f in imglist]
    img.save(fp=saveloc+'/zombies.gif',
             format='GIF',
             append_images=imgs,
             save_all=True,
             duration=1000,
             loop=0)

def initialize(G,p=0.3):
    """
    FUNCTION initialize
        initialize original Zombies in graph
    ARGUMENTS
        G:  networkx graph    city to simulate, no zombies assigned
        p:  float in [0,1]    probability for that a node is initially a zombie
    RETURNS
        G:  networkx graph    city to simulate, initialized with zombies
    """
    for v in G:
        G.nodes[v]['zombie']  = np.random.binomial(1,p)
        G.nodes[v]['time']    = None
    return G


def zombie_spread(G,  timesteps    = 10,
                      rule         = 'target_set_selection',
                      update_graph = False,
                      save_images  = True,
                      show_images  = True,
                      anim_images  = True):
    """
    FUNCTION zombie_spread
        model the zombie spread according to specified color changing rule on a given graph
    ARGUMENTS
        G:            networkx graph    city to simulate
        timesteps:    int               number of days to simulate
        rule:         string            name of color changing rule to follow
        update_graph: bool              if True, drop edges if neighbors are Zombies (Part 3.4)
        save_images:  bool              if True, save images to file
        show_images:  bool              if True, show images as output
        anim_images:  bool              if True and save_images == True, create gif from saved images
    """
    dirloc = rule
    imglist = []
    if save_images:
        if update_graph:
            dirloc += '/dynamic'
        else:
            dirloc += '/static'
        ! mkdir -p $dirloc

    G = initialize(G)
    pos = nx.layout.kamada_kawai_layout(G)

    for t in range(timesteps):
        draw_and_save(G, pos, dirloc+'/zombies-'+str(t), imglist, save_images, show_images)
        if update_graph:
            ###G = update_edges(G)
            draw_and_save(G, pos, dirloc+'/zombies-'+str(t)+'-edges', imglist, save_images, show_images)
        G = update_color(G, t, rule=rule)

    if anim_images and save_images:
        animate(imglist, dirloc)

    return G

"""### Color Changing Rules"""

###
### Part 3.2: Color Changing Rules
###
def update_color(G, time, rule='target_set_selection'):
    nextG = G.copy()
    if rule == 'target_set_selection':
       for node in G:
           infected_neighbors = 0
           for neighbor in G.neighbors(node):
               if G.nodes[neighbor]['zombie'] == 1:
                  infected_neighbors += 1
           if infected_neighbors >= 2:
              nextG.nodes[node]['zombie'] = 1
    elif rule == 'stochastic':
         for node in G:
           infected_neighbors = 0
           for neighbor in G.neighbors(node):
               if G.nodes[neighbor]['zombie'] == 1:
                  infected_neighbors += 1
           p = infected_neighbors / (G.degree(node) + 1)
           if np.random.binomial(1,p) == 1:
              nextG.nodes[node]['zombie']  = 1
    elif rule == 'deterministic':
         length = 0
         for node in G:
           infected_neighbors = 0
           for neighbor in G.neighbors(node):
               if G.nodes[neighbor]['zombie'] == 1:
                  infected_neighbors += 1
               length += 1
           if infected_neighbors/length > 1/3:
              nextG.nodes[node]['zombie'] = 1
           length = 0

    return nextG

G1 = nx.random_lobster(25, 0.8, 0.8, seed=10)
for k in range(25):
    i = np.random.randint(min(G1.nodes), max(G1.nodes)+1, dtype=np.int)
    j = np.random.randint(min(G1.nodes), max(G1.nodes)+1, dtype=np.int)
    if i != j:
        G1.add_edge(i,j)

zombie_spread(G1, rule = 'target_set_selection')
#zombie_spread(G1, rule = 'stochastic')
#zombie_spread(G1, rule = 'deterministic')

"""### A New Finding"""

###
### Part 3.4: A New Finding
###
def update_edges(G, p=0.1):
    nextG = G.copy()

    #
    # your code here
    #

    return nextG

"""Test on a model city with the cell below:"""

n_timesteps = 10
n_nodes     = 50

WSG = nx.watts_strogatz_graph(n_nodes, 6, 0.1, seed=10)
G = zombie_spread(WSG,  timesteps    = n_timesteps,
                        rule         = 'stochastic',
                        update_graph = False,
                        show_images  = False,
                        save_images  = True,
                        anim_images  = True)