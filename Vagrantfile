Vagrant.configure("2") do |config|

  config.vm.define "postgres" do |v|
    v.vm.provider "docker" do |d|
      d.image = "library/postgres:9.4"
      d.create_args = ["-p", "5432:5432", "-e", "POSTGRES_PASSWORD=postgres"]
    end
  end

  config.vm.define "rabbitmq" do |v|
    v.vm.provider "docker" do |d|
      d.image = "library/rabbitmq"
      d.create_args = ["--hostname=cdws", "-p", "5672:5672", "-e", "RABBITMQ_DEFAULT_VHOST=cdws"]
    end
  end

end