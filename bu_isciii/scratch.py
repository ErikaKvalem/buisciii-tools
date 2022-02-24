#!/usr/bin/env python
"""
=============================================================
HEADER
=============================================================
INSTITUTION: BU-ISCIII
AUTHOR: Sara Monzon; Sarai Varona
MAIL: smonzon@isciii.es; s.varona@isciii.es
CREATED: 24-02-2022
DESCRIPTION:
OPTIONS:

USAGE:

REQUIREMENTS:

TO DO:
    -copy_scratch: Change rsync to the one in the slurm hpc
================================================================
END_OF_HEADER
================================================================
"""
# Generic imports
import os
import subprocess
import logging

import rich

# Local imports
import bu_isciii
import bu_isciii.utils
from bu_isciii.drylab_api import RestServiceApi

log = logging.getLogger(__name__)
stderr = rich.console.Console(
    stderr=True,
    style="dim",
    highlight=False,
    force_terminal=bu_isciii.utils.rich_force_colors(),
)


class Scratch:
    def __init__(
        self,
        resolution_id=None,
        service_dir=None,
        tmp_dir=None,
    ):
        if resolution_id is None:
            self.resolution_id = bu_isciii.utils.prompt_resolution_id()
        else:
            self.resolution_id = resolution_id

        if service_dir is None:
            self.service_dir = bu_isciii.utils.prompt_service_dir_path()
        else:
            self.service_dir = service_dir

        if tmp_dir is None:
            self.tmp_dir = bu_isciii.utils.prompt_tmp_dir_path()
        else:
            self.tmp_dir = tmp_dir

        rest_api = RestServiceApi("http://iskylims.isciiides.es/", "drylab/api/")
        self.resolution_info = rest_api.get_request(
            "resolution", "resolution", self.resolution_id
        )
        self.service_folder = self.resolution_info["resolutionFullNumber"]
        self.scratch_path = os.path.join(
            tmp_dir, self.tmp_dir, self.service_folder
        )

    def copy_scratch(self):
        stderr.print("[blue]I will copy the service from %s" % self.service_dir)
        stderr.print("[blue]to %s" % self.scratch_path)
        if self.service_folder in self.service_dir:
            rsync_command = "rsync -rlv " + self.service_dir + " " + self.tmp_dir
            # rsync_command = "srun rsync -rlv "+self.service_dir+" "+self.tmp_dir
            try:
                subprocess.run(rsync_command, shell=True, check=True)
                out_file = os.path.join(self.tmp_dir, self.scratch_path, "DOC", "service_info.txt")
                f = open(out_file, "a")
                f.write("Temporal directory: "+self.scratch_path+"\n")
                f.write("Origin service directory: "+self.service_dir+"\n")
                f.close()
            except OSError:
                stderr.print(
                    "[red]ERROR: Copy of the directory %s failed" % self.service_dir,
                    highlight=False,
                )
            else:
                stderr.print(
                    "[green]Successfully copyed the directory to %s" % self.scratch_path,
                    highlight=False,
                )
        else:
            log.error(
                f"Directory path not the same as service resolution. Skip folder copy '{self.service_dir}'"
            )
            stderr.print(
                "[red]ERROR: Directory "
                + self.service_dir
                + " not the same as "
                + self.service_folder,
                highlight=False,
            )
        return True

    def revert_copy_scratch(self):
        stderr.print("[blue]I will copy the service from %s" % self.scratch_path)
        stderr.print("[blue]to %s" % self.service_dir)
