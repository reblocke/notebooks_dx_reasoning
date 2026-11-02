"""Recreated mathematical storyboard reference, not a Manim film frame."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'diagnostic-goal-06-reference',
                     'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
p=np.linspace(0,1,401);x=np.linspace(-4,4,401)
fig,axes=plt.subplots(1,3,figsize=(15,5),layout='constrained')
ax=axes[0]
ax.plot(p,p,':',color='gray',label='Identity')
ax.plot(p,3*p/(1+2*p),color='#0072B2',label='Positive: LR = 3')
ax.plot(p,p/(2-p),'--',color='#D55E00',label='Negative: LR = 0.5')
ax.scatter([.1,.5,.9],[.25,.75,27/28],color='#0072B2')
ax.set(xlim=(0,1),ylim=(0,1),xlabel='Pretest probability p',ylabel='Post-test probability q',title='1. One coherent probability leaf')
ax.set_aspect('equal');ax.legend(loc='lower right',fontsize=9)
ax=axes[1]
for lr,style,color in [(1,':','gray'),(3,'-','#0072B2'),(.5,'--','#D55E00')]:
    ax.plot(x,x+np.log(lr),style,color=color,label=f'LR = {lr:g}')
ax.set(xlim=(-4,4),ylim=(-4,4),xlabel='Pretest log odds X',ylabel='Post-test log odds Y',title='2. Both axes change coordinates')
ax.set_aspect('equal');ax.legend(loc='lower right',fontsize=9)
ax=axes[2]
ax.axhline(0,color='gray',lw=1)
ax.plot(p,5*p-1,color='#0072B2',label='B = 4, C = 1')
ax.plot(p,8*p-4,'--',color='#D55E00',label='B = 4, C = 4')
ax.axvline(.25,color='gray',ls=':');ax.scatter([.25,.25],[.25,-2],color=['#0072B2','#D55E00'])
ax.scatter([.2,.5],[0,0],color=['#0072B2','#D55E00'])
ax.set(xlim=(0,1),ylim=(-4.3,4.3),xlabel='Probability at the decision',ylabel='EU(act) − EU(defer)',title='3. Consequences set the threshold')
ax.legend(loc='upper left',fontsize=9)
fig.suptitle('Synthetic mathematical storyboard reference • newly reconstructed from Goal 06 formulas',fontsize=14)
folder=Path(__file__).resolve().parent
fig.savefig(folder/'06_leaf_logodds_utility_reference.png',dpi=170)
fig.savefig(folder/'06_leaf_logodds_utility_reference.svg',metadata={'Date':None})
svg=folder/'06_leaf_logodds_utility_reference.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
