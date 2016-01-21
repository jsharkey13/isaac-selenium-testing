Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  config.vm.box = "ubuntu/trusty64"
  config.vm.network "private_network", type: "dhcp"
  config.vm.synced_folder ".", "/isaac-selenium-testing"

   config.vm.provider "virtualbox" do |vb|
     # Display the VirtualBox GUI when booting the machine
     # vb.gui = true
  
     # Customize the amount of memory on the VM:
     vb.memory = "4096"
     vb.cpus = 2
     vb.name = "isaac-selenium-tester"
   end

  config.vm.provision :shell, path: "setup.sh"

  config.ssh.forward_agent = true
  
end
