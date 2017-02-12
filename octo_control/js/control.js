$(function() {
    function ControllerViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];
        self.connection = parameters[1];

        self.onBeforeBinding = function () {
            
        };

        self.isConnected = ko.computed(function() {
            return self.connection.loginState.isUser();
        });

        self.handleIO = function(data, event){
            $.ajax({
                    type: "GET",
                    dataType: "json",
                    data: {"io": data[0], "status": data[1]},
                    url: "/plugin/enclosure/setIO",
                    async: false
            });
        }
    }

    ADDITIONAL_VIEWMODELS.push([
        ControllerViewModel, 
        ["settingsViewModel","connectionViewModel"],
        [document.getElementById("tab_plugin_controller")]
    ]);
});

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

