
$(window).ready(()=> {
    /**
     * Custom context menu for displaying data
     * */
    window.contextMenu = $.contextMenu({

        selector: "[id^=tree] span.fancytree-title",
        build: function ($triggeredElement, e) {
            return {
                items: {
                    "cut": {
                        name: "Cut", icon: "cut",
                        callback: function (key, opt) {
                            let node = $.ui.fancytree.getNode(opt.$trigger);

                            alert("Clicked on " + key + " on " + node);
                        }
                    },

                    "copy": {name: "Copy", icon: "copy"},
                    "paste": {name: "Paste", icon: "paste", disabled: true},
                    "separator": "----",
                    "edit": {name: "Edit", icon: "edit", disabled: true},
                    "delete": {name: "Delete", icon: "delete", disabled: true},
                    "more": {
                        name: "More", items: {
                            "shortcuts": {
                                name: "Shortcuts",
                                callback(key, opt) {
                                    alert('');
                                    $('#modalShortcuts').modal('show');
                                }
                            },
                            "info": {
                                name: "Information",
                                callback(key, opt) {
                                    alert('');

                                    $('#confirmationWindow').modal('show');
                                }
                            }
                        }
                    }
                },
                callback: function (itemKey, opt) {
                    console.log('hi');
                }
            };
        }

    });
});