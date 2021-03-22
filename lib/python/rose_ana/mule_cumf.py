#*********************************COPYRIGHT*************************************
# (c) Crown copyright 2017 Met Office. All rights reserved.
#
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#*********************************COPYRIGHT*************************************
import os
import re
import mule
from StringIO import StringIO
from um_utils.cumf import (
    UMFileComparison, summary_report, full_report, COMPARISON_SETTINGS,
    _print_lookup)
import mule.stashmaster
from rose.apps.rose_ana import AnalysisTask
from rose import TYPE_LOGICAL_VALUE_TRUE

_COMPONENT_NAMES = (["fixed_length_header"] +
                    [comp[0] for comp in mule.UMFile.COMPONENTS] +
                    ["lookup"])

# For rose_ana we want to use the suite's STASHmaster instead of the centrally
# installed one (the user may have made required changes to it)
um_dir = "UM_INSTALL_DIR"
if um_dir in os.environ:
    mule.stashmaster.STASHMASTER_PATH_PATTERN = (
        re.sub(r"UMDIR", um_dir, mule.stashmaster.STASHMASTER_PATH_PATTERN))


class MuleCumf(AnalysisTask):
    """Compare two UM files using mule-cumf."""
    def run_analysis(self):
        """Main analysis routine called from rose_ana."""
        self.process_opt_files()
        self.process_opt_kgo()
        self.process_opt_ignores()
        self.process_opt_misc()
        # Deal with any unexpected options
        self.process_opt_unhandled()

        # Currently this analysis class can only handle comparing two files
        if len(self.files) != 2:
            raise ValueError("Must specify exactly two files for comparison.")

        self.perform_comparison()
        self.update_kgo()

    def perform_comparison(self):
        """Compare the files using mule-cumf."""
        # Turn the filenames into their absolute equivalents
        file1 = os.path.abspath(self.files[0])
        file2 = os.path.abspath(self.files[1])

        # Identify which of the two files is the KGO file
        if self.kgo is not None:
            kgo_file = [file1, file2][self.kgo]
            # If this file is missing, no comparison can be performed; it
            # could be that this task is brand new
            if not os.path.exists(kgo_file):
                # Report the filenames (with paths) - do this here rather
                # than in the non-error case because when successful
                # mule cumf prints the filenames anyway
                for ifile, fname in enumerate(self.files):
                    self.reporter(
                        "File {0}: {1}".format(
                            ifile + 1, os.path.abspath(self.files[ifile])))
                self.reporter(
                    "KGO File (file {0}) appears to be missing"
                    .format(self.kgo + 1), prefix="[FAIL] ")
                # Note that by exiting early this task counts as failed
                return

        # Load them using Mule - if either file doesn't appear to be
        # a recognised file type, this will abort... if it is recognised but
        # fails to validate, a warning will be raised and it may fail later.
        # However rose_ana will catch this and report to the user if needed.
        self.umf1 = mule.load_umfile(file1)
        self.umf2 = mule.load_umfile(file2)

        if self.prognostic_only:
            self.select_prognostic_fields()

        # Create the comparison object using Mule cumf
        self.compare = UMFileComparison(self.umf1, self.umf2)

        # If the comparison was successful, nothing more needs to be done
        if self.compare.match:
            self.passed = True
            # Capture the output from cumf's summary output and put into
            # the rose_ana output
            prefix = "[INFO] "
            self.write_output_info(prefix=prefix)
        else:
            # Capture the output from cumf's summary output and put into
            # the rose_ana output
            prefix = "[FAIL] "
            self.write_output_info(prefix=prefix)

            # Get a reference to the log directory
            log_root = os.path.dirname(os.environ["ROSE_TASK_LOG_ROOT"])

            # Create a suitable filename for the cumf output using the
            # task name (so it'll be unique)
            basename = self.get_output_basename()

            # Write the full results of the cumf comparison
            self.write_full_output(log_root, basename)

            # Write a summary of the field differences
            self.write_summ_output(log_root, basename)

    def update_kgo(self):
        """
        Update the KGO database with the status of any files marked by the
        kgo_file option (i.e. whether they have passed/failed the test.)

        """
        if self.kgo is not None and self.kgo_db is not None:
            self.reporter(
                "Adding entry to KGO database (File {0} is KGO)"
                .format(self.kgo + 1), prefix="[INFO] ")
            # Take the KGO file
            kgo_file = self.files[self.kgo]
            # The other file is the suite file
            suite_file = list(self.files)
            suite_file.remove(kgo_file)

            # Set the comparison status
            status = ["FAIL", " OK "][self.passed]

            # Update the database
            self.kgo_db.enter_comparison(
                self.options["full_task_name"],
                os.path.abspath(kgo_file),
                os.path.abspath(suite_file[0]),
                status, "Compared using Mule cumf")

    def process_opt_files(self):
        """Process the files option; a list of one or more filenames."""
        # Get the file list from the options dictionary
        files = self.options.pop("files", None)
        # Make sure it appears as a sensible list
        if files is None:
            files = []
        elif isinstance(files, str):
            files = [files]
        self.files = files

    def process_opt_kgo(self):
        """
        Process the KGO option; an index indicating which file (if any) is
        the KGO (Known Good Output) - this may be needed later to assist in
        updating of test results.

        """
        # Get the kgo index from the options dictionary
        kgo = self.options.pop("kgo_file", None)
        # Parse the kgo index
        if kgo is not None:
            if kgo.strip() == "":
                kgo = None
            elif kgo.isdigit():
                kgo = int(kgo)
                if kgo > len(self.files) - 1:
                    msg = "KGO index cannot be greater than number of files"
                    raise ValueError(msg)
                self.reporter("KGO is file {0}".format(kgo + 1))                
            else:
                msg = ("KGO index not recognised; should be either a digit or "
                       "left blank")
                raise ValueError(msg)
        self.kgo = kgo

    def process_opt_ignores(self):
        """Process ignore options, which control how mule-cumf operates."""
        for option in self.options.keys():
            if (option.startswith("ignore-")
                    and option[7:] in _COMPONENT_NAMES):
                values = self.options.pop(option)
                name = option.split("-")[1]
                indices = [int(index) for index in values.split()]
                COMPARISON_SETTINGS["ignore_templates"][name] = indices
                self.reporter(
                    "Ignoring indices {0} of {1}".format(indices, option[7:]))
                continue
            if option == "ignore_missing":
                value = self.options.pop(option)
                if value.lower() == "true":
                    COMPARISON_SETTINGS["ignore_missing"] = True
                self.reporter("Ignoring positional header data")

        # Check to see if user's config has flag set to bypass version check
        # (mainly used when installing the new release)
        bypass_version_check = self.config.get(
            "bypass-version-check", ".false.")

        if bypass_version_check != TYPE_LOGICAL_VALUE_TRUE:
            return

        # Add fixed length header 12 (model version number) 
        # to the list of ignored indices
        COMPARISON_SETTINGS["ignore_templates"]["fixed_length_header"] = (
            COMPARISON_SETTINGS["ignore_templates"]["fixed_length_header"] 
                + [12,])

        # if no loopkup items already in ignored templates then initialise
        if "lookup" not in COMPARISON_SETTINGS["ignore_templates"]:
            COMPARISON_SETTINGS["ignore_templates"]["lookup"] = []

        # Add lookup 38 lbsrc (model version number) to list of ignored
        # indices
        COMPARISON_SETTINGS["ignore_templates"]["lookup"] = (
            COMPARISON_SETTINGS["ignore_templates"]["lookup"] 
                + [38,])

    def process_opt_misc(self):
        """
        Process other options that could be specified by rose_ana task
        """
        prog_str = self.options.pop('prognostic_only', ".false.")
        if prog_str not in (".false.", ".true."):
            msg = "Prognostic only option must be '.false.' or '.true.'"
            raise ValueError(msg)
        self.prognostic_only = {'.false.': False, '.true.': True}.get(prog_str)

    def select_prognostic_fields(self):
        file1_is_dump = self.umf1.fixed_length_header.dataset_type in (1, 2)
        file2_is_dump = self.umf2.fixed_length_header.dataset_type in (1, 2)
        if not (file1_is_dump and file2_is_dump):
            msg = 'Prognostic-only option only valid for dump type files'
            raise ValueError(msg)

        msg1 = 'Prognostics only option selected\n'
        self.reporter(msg1, prefix='[INFO] ')

        def do_select(umf,fnum):
            total_fields = len(umf.fields)
            total_prog_fields = umf.fixed_length_header.total_prognostic_fields

            diff1 = total_fields - total_prog_fields
            msg1 = ('file {fnum}\n'
                    'Total fields = {total}\n'
                    'Prognostic fields = {progs}\n'
                    '{diff} fields not included\n')
            msg1 = msg1.format(total=total_fields,
                                progs=total_prog_fields,
                                diff=diff1,
                                fnum=fnum)
            self.reporter(msg1, prefix='[INFO] ')

            return umf.fields[:total_prog_fields]

        self.umf1.fields = do_select(self.umf1,1)
        self.umf2.fields = do_select(self.umf2,2)


    def write_output_info(self, prefix=""):
        """
        Generate the normal mule-cumf summary output, but redirect it
        to the Rose reporter along with the rest of the task output.
        """
        strbuffer = StringIO()
        summary_report(self.compare, stdout=strbuffer)
        lines = strbuffer.getvalue().strip("\n")
        self.reporter(lines, prefix=prefix)

    def get_output_basename(self):
        """
        Generate a suitable name for the output files; this is based on
        the task name within the rose_ana app.
        """
        cumf_base_name = self.options["full_task_name"]
        cumf_base_name = re.sub(r"[() ]", r"_", cumf_base_name)
        if cumf_base_name.endswith("_"):
            cumf_base_name = cumf_base_name[:-1]
        return "ana." + cumf_base_name

    def write_full_output(self, log_root, basename):
        """
        Generate the normal mule-cumf full output, but redirect it
        to a file - make it behave like a simple HTML file so that
        it displays nicely if viewed in a browser.
        """
        cumf_full_name = basename + "_full.html"
        full_log = os.path.join(log_root, cumf_full_name)
        with open(full_log, "w") as log:
            log.write('<!DOCTYPE html><html lang="en">'
                      '<head></head><body><pre>\n')
            full_report(self.compare, stdout=log)
            log.write("</pre></body></html>")

        # Print the path to the log output file in the task output
        full_link = (
            '**Cumf Full Report Output**  : {0}/{1}'
            .format(log_root, cumf_full_name))
        self.reporter(full_link, prefix="[FAIL] ")

    def write_summ_output(self, log_root, basename):
        """
        Generate a simple html file which displays a summary of any
        field differences, for display in a browser.
        """
        # If there were no data mis-matches, exit
        data_matches = [
            comp.data_match for comp in self.compare.field_comparisons]
        if all(data_matches):
            return

        cumf_summ_name = basename + "_summ.html"
        summ_log = os.path.join(log_root, cumf_summ_name)
        with open(summ_log, "w") as log:
            msg = 'Field data differences for "' + basename + '":'
            log.write('<!DOCTYPE html><html lang="en">'
                      '<head></head><body><pre>{0}<table>\n'.format(msg))

            for icomp, comparison in enumerate(self.compare.field_comparisons):
                if not comparison.data_match:
                    # Try to get the stash name for the output
                    if comparison.stash is not None:
                        stash_name = comparison.stash.name
                    else:
                        stash_name = (
                            "UNKNOWN stash {0}".format(comparison.lbuser4))

                    # A simple throwaway formatter for the rms values
                    def convrms(rms):
                        if rms < 0.01:
                            rms = "< 0.01%"
                        else:
                            rms = "{0:6.2f}%".format(rms)
                        return rms

                    rms1 = convrms(comparison.rms_norm_diff_1)
                    rms2 = convrms(comparison.rms_norm_diff_2)

                    info = ("<tr><td> Field Comparison {0} </td>"
                            "<td> {1:37s} </td>"
                            "<td> Max Diff ({2:12e}) </td>"
                            "<td> RMS / File1 ({3}) </td>"
                            "<td> RMS / File2 ({4}) </td></tr>"
                            .format(icomp + 1, stash_name,
                                    comparison.max_diff,
                                    rms1, rms2))
                    log.write(info + "\n")
            log.write("</table></pre></body>"
                      "<style>"
                      "table{width:100%; border-collapse:collapse;}"
                      "tr:hover{background:#eeeeee;}"
                      "td{border-bottom: 2px solid #eeeeee;}"
                      "</style></html>")

        # Print the path to this summary output file in the task output
        summ_link = (
            '**Cumf Field Summary Output**: {0}/{1}'
            .format(log_root, cumf_summ_name))
        self.reporter(summ_link, prefix="[FAIL] ")
