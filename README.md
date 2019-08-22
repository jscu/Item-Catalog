# Item Catalog Project
This application allows anyone to view items that are associated with a category. User can login via Google Sign-in and enjoy the privilege of creating, editing and deleting his/her own items.


### Structure
```
.
├── application.py
├── client_secrets.json
├── create_test_data.py
├── init_db.py
├── models.py
├── README.md
├── static
│   └── bootstrap.min.css
│   └── templatemo_style.css
└── templates
    ├── add_item.html
    ├── delete_item.html
    ├── edit_item.html
    ├── index.html
    ├── layout.html
    ├── login.html
    ├── view_individual_item.html
    ├── view_items.html
```

## Instructions to run this application

1. Install [Vagrant](https://www.vagrantup.com/downloads.html) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

2. Clone the fullstack-nanodegree-vm from [here](https://github.com/udacity/fullstack-nanodegree-vm)

3. `cd` to `vagrant/` and type `vagrant up` to start the VM. This operation might take a while

4. Run `vagrant ssh` to ssh into the VM and `cd /vagrant` to go to the shared directory

5. Unzip all the files of this project and put them under `/vagrant`

6. Create the database, tables and populate with test data
    ```sh
    python create_test_data.py
    ```

7. Start the application at `http://localhost:8000` with
    ```sh
    python application.py
    ```