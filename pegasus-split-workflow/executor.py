#!/usr/bin/env python
# encoding: UTF-8
import time, os, re, commands, json, glob, shutil, csv

class PegasusWorkflow:

  def __init__(self):
    self.base_directory = ""
    self.wf_label = "split"
    self.status = dict()

  def submit(self):
    cmd = "sh generate_dax.sh wf.dax"
    output = commands.getoutput(cmd)
    print "DAX generation:", output

    cmd = "sh plan_dax.sh wf.dax"
    output = commands.getoutput(cmd)
    print "Workflow submitted:", output

    started = False
    for line in output.split("\n"):
      if "Your workflow has been started and is running" in line:
        started = True
      if started and "pegasus-status -l" in line:
        self.base_directory = line.split()[-1]
        break

    print "Base directory for workflow execution is:", self.base_directory

    return len(self.base_directory) > 0

  def update_status(self):
    pegasus_status = commands.getoutput("pegasus-status -l %s" % self.base_directory)
    self.status = self.parse_pegasus_status(pegasus_status)

    return self.status

  def is_running(self):
    return ("STATE" in self.status and self.status["STATE"] == "Running") or (
        "%s-0" % self.wf_label in self.status and self.status["%s-0" % self.wf_label]["status"] == "Run"
    )

  def failed(self):
    return "STATE" in self.status and self.status["STATE"] == "Failure"

  def summary(self):
    return commands.getoutput("pegasus-analyzer %s" % self.base_directory)

  def full_results(self, file_name):
    results = dict()

    results["summary"] = self.summary()
    results["file_name"] = file_name

    jobs = self.jobs_statistics()
    for job_name in jobs:
      results[job_name] = jobs[job_name]

    files = self.output_files_statistics()
    for key in files:
      results[key] = files[key]

    return results

  def jobs_statistics(self):
    while True:
      cmd = "pegasus-statistics -f csv -s jb_stats %s" % (self.base_directory)
      print "Command:", cmd

      output = commands.getoutput(cmd)
      print "Output:", output

      time.sleep(15)

      if os.path.exists("%s/statistics/jobs.csv" % self.base_directory):
        return self.parse_pegasus_job_statistics("%s/statistics/jobs.csv" % self.base_directory)
      else:
        time.sleep(10)

  # find out how long jobs execution took
  def parse_pegasus_job_statistics(self, file_path):
    jobs = {}

    fp = open(file_path)
    rdr = csv.DictReader(filter(lambda row: row[0] != '#', fp))
    job_idx = None
    kickstart_idx = None

    for row in rdr:
      print row

      if "Job" in row:
        jobs[ row["Job"].replace(".", "_") ] = float(row["Kickstart"])
      elif None in row:
        if job_idx is None:
          job_idx = row[None].index("Job")
          kickstart_idx = row[None].index("Kickstart")
        else:
          jobs[ row[None][job_idx].replace(".", "_") ] = float(row[None][kickstart_idx])

      fp.close()

    return jobs        


  # find out how big are output files
  def output_files_statistics(self):
    output_dir = "split-workflow/output"
    file_size_in_mb = {}

    # iterater through files and execute
    for absolute_file_path in glob.glob(output_dir + "/*"):
      if absolute_file_path == "." or absolute_file_path == "..":
        continue

      file_name = absolute_file_path.split("/")[-1]

      # file_size_in_mb[file_name.replace(".", "_") + "-size"] = os.stat(absolute_file_path).st_size / (1024*1024)
      file_size_in_mb[file_name.replace(".", "_") + "-content"] = commands.getoutput("cat " + absolute_file_path)

    return file_size_in_mb    

  def pack_output_files(self):
    commands.getoutput("cp -R split-workflow/output .")
    print commands.getoutput("tar czvf output.tar.gz output")

# private
  def parse_pegasus_status(self, status_output):
    parsed_output = dict()

    parse_job_mode = False
    parse_summary_mode = False
    char_pattern = re.compile("([a-zA-Z])")

    for line in status_output.split("\n"):
      if line.startswith("STAT"):
        parse_job_mode = True
      elif line.startswith("Summary"):
        parse_job_mode = False
      elif parse_job_mode:
        line_tokens = line.split()
        status, in_state, job = line_tokens[0:3]

        ch_index = char_pattern.search(job)
        if ch_index is None:
          print "Couldn't parse: ", line
        else:
          job = job[ch_index.start():]
          parsed_output[job] = {"status": status, "in_state": in_state}

      elif line.startswith("UNRDY"):
        parse_summary_mode = True
      elif parse_summary_mode:
        summary = line.split()
        if len(summary) >= 9:
          parsed_output["%DONE"] = summary[7]
          parsed_output["STATE"] = summary[8]

    return parsed_output


def main():
  with open('input.json') as data_file:
    data = json.load(data_file)
    file_name_to_parse = data["file_to_parse"]

  os.chdir("split-workflow")
  wf = PegasusWorkflow()

  if not wf.submit():
    print "Workflow not submitted successfully"

    with open("output.json", "w") as f:
      json.dump({"status": 'error', "reason": "Workflow not submitted successfully"}, f)
      exit(1)

  time.sleep(10)

  os.chdir("..")

  while wf.update_status() and wf.is_running():
    progress = {"status": 'ok', "results": {"file": file_name_to_parse, "status": wf.status}}

    with open("intermediate_result.json", "w") as f:
      json.dump(progress, f)

    time.sleep(20)

  print "Workflow is not running anymore:", wf.status

  time.sleep(30)

  with open("output.json", "w") as f:
    if wf.failed():
      json.dump({"status": 'error', "reason": wf.summary()}, f)
    else:
      json.dump({"status": 'ok', "results": wf.full_results(file_name_to_parse)}, f)
      wf.pack_output_files()


main()
