from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os

from jupyter_client import KernelManager
from nbformat.v4 import output_from_msg
from . import misc
try:
    from queue import Empty  # Py 3
except ImportError:
    from Queue import Empty # Py 2


class JupyterKernelClient:
    def __init__(self):
        self.manager = KernelManager(kernel_name='python3')
        self.kernel = self.manager.start_kernel()
        self.client = self.manager.client()
        self.client.start_channels()

def stop(kernel_client):
    kernel_client.client.stop_channels()
    kernel_client.manager.shutdown_kernel()


def run_cell(kernel_client, source, timeout=120):
    if misc.option('verbose-execute'):
        print("Executing cell:\n{}\nExecution in\n{}\n".format(source, os.getcwd()))

    # Adapted from nbconvert.ExecutePreprocessor
    # Copyright (c) IPython Development Team.
    # Distributed under the terms of the Modified BSD License.
    msg_id = kernel_client.client.execute(source)
    # wait for finish, with timeout
    while True:
        try:
            msg = kernel_client.client.shell_channel.get_msg(timeout=timeout)
        except Empty:
            print("Timeout waiting for execute reply", timeout)
            print("Tried to run the following source:\n{}".format(source))
            try:
                exception = TimeoutError
            except NameError:
                exception = RuntimeError
            raise exception("Cell execution timed out")

        if msg['parent_header'].get('msg_id') == msg_id:
            if misc.option('verbose-execute'):
                print("Wrong message id")
            break
        else:
            if misc.option('verbose-execute'):
                print("Not our reply")
            continue

    outs = []
    execution_count = None

    while True:
        try:
            # We've already waited for execute_reply, so all output
            # should already be waiting. However, on slow networks, like
            # in certain CI systems, waiting < 1 second might miss messages.
            # So long as the kernel sends a status:idle message when it
            # finishes, we won't actually have to wait this long, anyway.
            msg = kernel_client.client.iopub_channel.get_msg(timeout=5)
        except Empty:
            if misc.option('verbose-execute'):
                print("Timeout waiting for IOPub output")
            break
        if msg['parent_header'].get('msg_id') != msg_id:
            if misc.option('verbose-execute'):
                print("Not output from our execution")
            continue

        if misc.option('verbose-execute'):
            print(msg)

        msg_type = msg['msg_type']
        content = msg['content']

        # set the prompt number for the input and the output
        if 'execution_count' in content:
            execution_count = content['execution_count']
            # cell['execution_count'] = content['execution_count']

        if msg_type == 'status':
            if content['execution_state'] == 'idle':
                if misc.option('verbose-execute'):
                    print("State is idle")
                break
            else:
                if misc.option('verbose-execute'):
                    print("Other status")
                continue
        elif msg_type == 'execute_input':
            continue
        elif msg_type == 'clear_output':
            outs[:] = []
            if misc.option('verbose-execute'):
                print("Request to clear output")
            continue
        elif msg_type.startswith('comm'):
            if misc.option('verbose-execute'):
                print("Output start with 'comm'")
            continue

        display_id = None
        if msg_type in {'execute_result', 'display_data', 'update_display_data'}:
            display_id = msg['content'].get('transient', {}).get('display_id', None)
            if msg_type == 'update_display_data':
                if misc.option('verbose-execute'):
                    print("Update_display_data doesn't get recorded")
                continue

        try:
            out = output_from_msg(msg)
        except ValueError:
            print("unhandled iopub msg: " + msg_type)

        outs.append(out)

        if misc.option('verbose-execute'):
            print("Cell execution result:\n{}\n".format(out))

    return outs, execution_count
