# ansible_phpipam
An inventory script I developed for querying a PHpipam DB and providing Ansible ready JSON output

Using this script has a couple requirements:

1. Ansible Automation Platform controller, Tower or AWX
2. Creating a Custom credential type that includes the following Env Injectors:
   
    `env:`
    
  `IPAM_DBHOST: '{{ host }}'`
  
  `IPAM_DBPASS: '{{ password }}'`
  
  `IPAM_DBUSER: '{{ username }}'`
 
  
3. You create a Project, then an Inventory with a source `from Project`
4. On the PhpIpam side: I am using custom fields in lieu of tags to filter IPAddresses that I want to manage.
    So there are custom_fields on IPAddresses and Subnets, so I can filter based on both. Your situation
    might differ, adjust the query accordingly.
5. Make sure the .py is executable
    
For testing this outside of AAP, it's as easy and running the script. However inside of AAP there are some hurdles,
since AAP utilizes containers at Job runtime you must do a few things. Mount the container or Execution Environment you intend
to use in the AAP Inventory Source, start a bash session within it, manually set the ENV variables then run it.

Provided you see JSON output, then it should work fine within AAP. 

In my situation I encountered a month's worth of problems that ultimately were resolved by changing the credential used, 
then switching back to the original. Even RH support had no clue why.
  
Something to note: The job can run inside AAP and if say there's an issue communicating with the DB, or the credentials 
supplied are incorrect or for whatever reason it cannot connect to teh database.. AAP's error (ansible-inventory actually)
will give no indication that there's an issue like that. My RH guy submitted an RFE to get the error handling tweaked for this
but for now it'll only return that it expected data on line 1, column 1 and got nothing.
