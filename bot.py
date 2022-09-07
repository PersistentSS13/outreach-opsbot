import discord
import os
import yaml

from kubernetes import client, config


# Discord auth token
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

# operating namespace
NAMESPACE = os.environ.get("NAMESPACE")

ADMIN_FILE = "admins.txt"

JOBS = {
    "restore-sql-backup": "./jobs/restore-sql-backup/job-restore-sql-backup.yaml",
}


def load_admins():
    with open(ADMIN_FILE) as f:
        return f.readlines()


class Commands:
    def __init__(self):
        self.commands = {
            "test": self.test,
            "jobs": self.jobs,
            "jobs_status": self.jobs_status,
            "create_job": self.create_job,
        }

    async def test(self, message):
        await message.channel.send('Hello!')

    async def jobs(self, message):
        '''lists creatable jobs'''
        await message.channel.send(f"{JOBS}")

    async def jobs_status(self, message):
        config.load_kube_config()
        v1 = client.BatchV1Api()

        send_str = "```Jobs status:\n"
        ret = v1.list_namespaced_job("persistent-outreach")
        send_str += "NAMESPACE\t\t\tSTART TIME\t\t\t\t\tJOB NAME\t\t\t\t\tTOTAL\tREADY\tFAILED\tSUCCEEDED\n"
        for i in ret.items:
            send_str += f"{i.metadata.namespace}\t{i.status.start_time}\t{i.metadata.name}\t{i.spec.completions}\t\t{i.status.ready or 0}\t\t{i.status.failed or 0}\t\t{i.status.succeeded or 0}\n"
        await message.channel.send(send_str + "```")
    
    async def create_job(self, message):
        config.load_kube_config()

        message_split = message.content.split(" ")

        if len(message_split) < 3:
            await message.channel.send(f"USAGE: create_job [job_name]")
            return

        job_name = message_split[2]
        job_path = JOBS.get(job_name)

        if job_path is None:
            await message.channel.send(f"No job definition found for: `{job_name}`")
            return
        
        if job_name == "restore-sql-backup":
            if len(message_split) != 4:
                await message.channel.send(f"USAGE: create_job restore-sql-backup [target_gcs_file] ")

            target_file = message_split[3]
            with open(job_path) as f:
                job_def = yaml.safe_load(f)
                job_def['spec']['template']['spec']['containers'][0]['env'][0]['value'] = target_file
                v1 = client.BatchV1Api()
                v1.create_namespaced_job(namespace=NAMESPACE, body=job_def)
                await message.channel.send(f"Job created: `{job_name}`")
                return
            
        await message.channel.send(f"Job doesn't appear to be implemented yet: `{job_name}`")
        return


def main():
    admins = load_admins()
    commands = Commands()

    intents = discord.Intents.default()
    discord_client = discord.Client(intents=intents)

    @discord_client.event
    async def on_message(message):
        if message.author == discord_client.user:
            return

        message_author_unique = f"{message.author.name}#{message.author.discriminator}"
        if message_author_unique not in admins:
            return

        print(f"{message.channel} - {message_author_unique} - {message.content}")
        message_split = message.content.split(" ")
        target_command = message_split[1]
        command_func = commands.commands.get(target_command)

        if command_func is not None:        
            await command_func(message)

    discord_client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()