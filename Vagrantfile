# -*- mode: ruby -*-
# vi: set ft=ruby :

# This Vagrantfile targets the vagrant-lxc provider. It should work on other providers given
# a relatively recent version of Vagrant, but your mileage may vary.

Vagrant.configure("2") do |config|
  config.vm.box = "precise64"

  # Forward a port to the development server
  config.vm.network :forwarded_port, guest: 8000, host: 8000, host_ip: '0.0.0.0'


  # Provision packages -- if you change this after creating the VM, just do "vagrant provision" to run it again
  config.vm.provision :shell, :inline => <<END
# Check if we need to perform a weekly upgrade - this also triggers initial provisioning
touch -d '-1 week' /tmp/.limit

# Install base packages
if [ /tmp/.limit -nt /var/cache/apt/pkgcache.bin ]; then
    apt-get -y remove puppet chef
    apt-get -y autoremove
    apt-get -y update
    apt-get -y dist-upgrade
    apt-get -y install htop tmux vim rsync 
    apt-get -y install libpcre3-dev
fi
rm /tmp/.limit

# Install Redis
if [ ! -x /usr/bin/redis-cli ]; then
    apt-get -y install redis-server
fi

# Install basic Python support
if [ ! -x /usr/bin/easy_install ]; then
    apt-get -y install python-dev python-setuptools
    sudo easy_install pip
    sudo pip install virtualenvwrapper 
    echo ". /usr/local/bin/virtualenvwrapper.sh" | tee -a ~vagrant/.bashrc
fi

# Build our virtualenv
if [ ! -d ~vagrant/.virtualenvs/yaki ]; then
    sudo -u vagrant bash /vagrant/provision.sh
fi

END
end
