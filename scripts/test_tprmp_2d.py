import sys
import argparse
import numpy as np
from os.path import join, dirname, abspath
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

ROOT_DIR = join(dirname(abspath(__file__)), '..')
sys.path.append(ROOT_DIR)
from tprmp.utils.loading import load  # noqa
from tprmp.visualization.demonstration import plot_demo  # noqa
from tprmp.visualization.dynamics import plot_potential_field, visualize_rmp # noqa
from tprmp.models.tp_rmp import TPRMP  # noqa
from tprmp.demonstrations.base import Demonstration  # noqa
from tprmp.demonstrations.manifold import Manifold  # noqa
from tprmp.demonstrations.frame import Frame  # noqa
from tprmp.demonstrations.quaternion import q_convert_wxyz, q_from_euler, q_convert_xyzw  # noqa

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description='Example run: python test_tprmp.py test.p')
parser.add_argument('task', help='The task folder', type=str, default='pick')
parser.add_argument('data', help='The data file', type=str, default='data.p')
args = parser.parse_args()

DATA_DIR = join(ROOT_DIR, 'data', 'tasks', args.task, 'demos')
data_file = join(DATA_DIR, args.data)
# parameters
oversteps = 50
dt = 0.01
NUM_COMP = 20
alpha, beta = 0., 0.
stiff_scale = 1.
tau = 1.
potential_method = 'quadratic'
optimize_method = 'flow'
d_min = 0.
d_scale = 1.
energy = 0.
sigma = 1.
var_scale = 1.
r = 0.01
res = 0.05
verbose = False
# load data
data = load(data_file)
demos = []
manifold = Manifold.get_euclidean_manifold(2)
for d in data:
    traj = np.stack(d)
    demo = Demonstration(traj, manifold=manifold, dt=dt)
    demo.add_frame_from_pose(traj[:, 0], 'start')
    demo.add_frame_from_pose(traj[:, -1], 'end')
    demos.append(demo)
plot_demo(demos, only_global=False, plot_quat=False, new_fig=True, new_ax=True, three_d=False, show=True)
# train tprmp
sample = demos[0]
frames = sample.get_task_parameters()
model = TPRMP(num_comp=NUM_COMP, name=args.task, sigma=sigma, stiff_scale=stiff_scale, tau=tau, potential_method=potential_method, d_scale=d_scale)
model.train(demos, optimize_method=optimize_method, alpha=alpha, beta=beta, d_min=d_min, energy=energy, var_scale=var_scale, verbose=verbose)
model.model.plot_model(demos, tagging=False, three_d=False)
plot_potential_field(model, frames, only_global=False, margin=0.5, res=res, new_fig=True, show=True)
# execution
x0, dx0 = np.array([0.5, 2.5]), np.zeros(2)
visualize_rmp(model, frames, x0, dx0, sample.traj.shape[1] + oversteps, dt, sample=sample, x_limits=[0., 4.], vel_limits=[-10., 10.])
input()
