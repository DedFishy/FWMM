const WIDTH = 9;
const HEIGHT = 34;


const availableWidgetList = document.getElementById("available-widget-list");
const widgetTree = document.getElementById("widget-tree");

var widgets = [];

// Helpers
async function getJSONFromPath(path) {
    const request = await fetch(path);
    const json = await request.json();
    return json

}

// Available Widget List
async function fetchInitial() {
    handleFullUpdate(await getJSONFromPath("/initial"));
}
async function constructAvailableWidgetList(available) {
    availableWidgetList.innerHTML = "";
    available.forEach((value, index, array) => {
        const widgetElement = document.createElement("div");
        widgetElement.className = "available-widget";
        widgetElement.innerText = value;
        widgetElement.draggable = true;
        widgetElement.widgetName = value;
        widgetElement.ondragstart = (event) => {event.dataTransfer.setData("widgetName", value);}
        availableWidgetList.appendChild(widgetElement);
    })
}

// Full Update
function checkWidgetDiff(newWidgetList) {
    if (newWidgetList.length != widgets.length) return true;
    var isChanged = false;
    newWidgetList.forEach((value, index, array) => {
        if (value["name"] != widgets[index]) {
            isChanged = true;
            return;
        }
    });
    return isChanged;
}
function handleFullUpdate(update) {
    console.log("Recieved an update!");
    console.log(update);
    if (checkWidgetDiff(update,["widgets"])) {
        widgetTree.innerHTML = "";
        update["widgets"].forEach((value, index, array) => {
            constructOneWidget(value);
        });
    }
    if (availableWidgetList.children.length != update["available"].length)
        constructAvailableWidgetList(update["available"]);

}

// Widget Tree
async function sendConfigUpdate(widgetIndex, name, newValue) {
    await getJSONFromPath("/updatewidgetconfig/" + widgetIndex + "/" + name + "/" + newValue)
}
async function sendTransformUpdate(widgetIndex, name, newValue) {
    await getJSONFromPath("/updatewidgettransform/" + widgetIndex + "/" + name + "/" + newValue)
}
async function createWidget(widget) {
    return await getJSONFromPath("/createwidget/" + widget)
}

widgetTree.ondragover = (event) => {event.preventDefault();}
widgetTree.ondrop = async (event) => {
    event.preventDefault();
    
    handleFullUpdate(await createWidget(event.dataTransfer.getData("widgetName")));
}

function constructOneWidget(widgetMetadata) {
    console.log("Rendering widget with metadata:")
    console.log(widgetMetadata)
    const widgetElement = document.createElement("div");
    widgetElement.className = "widget-tree-widget-container";

    const widgetDropdownIndicator = document.createElement("div");
    widgetDropdownIndicator.className = "widget-tree-dropdown-indicator";
    widgetElement.appendChild(widgetDropdownIndicator);

    const widgetNameIndicator = document.createElement("div");
    widgetNameIndicator.className = "widget-tree-name-indicator";
    widgetNameIndicator.innerText = widgetMetadata["name"];
    widgetElement.appendChild(widgetNameIndicator); 

    const widgetTransform = document.createElement("div");
    widgetTransform.className = "widget-tree-transform";
    widgetTransform.appendChild(constructConfigItem(widgetMetadata["index"], "X", {
        "item_type": 1,
        "value": 0,
        "minimum": 0,
        "maximum": 10
    },
    true))
    widgetTransform.appendChild(constructConfigItem(widgetMetadata["index"], "Y", {
        "item_type": 1,
        "value": 0,
        "minimum": 0,
        "maximum": 35
    },
    true))
    widgetTransform.appendChild(constructConfigItem(widgetMetadata["index"], "Rotation", {
        "item_type": 6,
        "value": 0,
        "options": [0, 90, 180, 270]
    },
    true))
    widgetElement.appendChild(widgetTransform);

    const widgetConfig = document.createElement("div");
    widgetConfig.className = "widget-tree-config";
    Object.keys(widgetMetadata["config"]).forEach((value, index, array) => {
        widgetConfig.appendChild(constructConfigItem(widgetMetadata["index"], value, widgetMetadata["config"][value], false));
    })
    widgetElement.appendChild(widgetConfig);

    widgetTree.appendChild(widgetElement);

    
}

function constructConfigItem(widgetIndex, name, meta, isTransform) {
    console.log(name, meta);
    const container = document.createElement("div");
    container.className = "widget-tree-config-item";

    const label = document.createElement("div");
    label.className = "widget-tree-config-item-label";
    label.innerText = name;
    container.appendChild(label);

    var input;
    var innerInput = undefined;
    switch (meta["item_type"]) {
        case 1: // Number (TODO: Make this show a range slider as well)
            input = document.createElement("input");
            input.type = "number";
            input.value = meta["value"];
            input.min = meta["minimum"];
            input.max = meta["maximum"];

            innerInput = document.createElement("input");
            innerInput.className = "number-input-slider";
            innerInput.type = "range";
            innerInput.min = meta["minimum"];
            innerInput.max = meta["maximum"];
            innerInput.value = meta["value"];
            console.log(name, meta["value"]);
            innerInput.onchange = (event) => {
                input.value = innerInput.value;
                input.onchange(undefined);
            };

            const incDecContainer = document.createElement("div");
            incDecContainer.className = "number-inc-dec-container";

            incButton = document.createElement("button");
            incButton.className = "number-inc-button";
            incButton.onclick = (event) => {input.value = Number(input.value) + 1; input.onchange(undefined);}
            incButton.innerText = "⮝"
            incDecContainer.appendChild(incButton);

            decButton = document.createElement("button");
            decButton.className = "number-dec-button";
            decButton.onclick = (event) => {input.value = Number(input.value) - 1; input.onchange(undefined);}
            decButton.innerText = "⮟"
            incDecContainer.appendChild(decButton);

            container.appendChild(innerInput);
            container.appendChild(incDecContainer);
            break;
        case 5:
            input = document.createElement("input");
            input.type = "checkbox";
            input.value = meta["value"];
            break;
        case 6: // Dropdown
            input = document.createElement("select");
            meta["options"].forEach((value, index, array) => {
                const option = document.createElement("option");
                option.value = value;
                option.innerText = value;
                if (value == meta["value"]) option.selected = true;
                input.appendChild(option);
            })
            break;
        default:
            input = document.createElement("div");
            input.innerText = "Unsupported item type!";
            break;
    }
    input.className = "widget-tree-config-item-input";
    input.onchange = (event) => {
        if (meta["item_type"] == 1) {
            console.log(meta, Number(input.value))
            if (Number(input.value) > meta["maximum"]) {
                input.value = meta["maximum"];
                return;
            }
            else if (Number(input.value) < meta["minimum"]) {
                input.value = meta["minimum"];
                return;
            }
        }
        if (innerInput) {innerInput.value = input.value}
        if (!isTransform) sendConfigUpdate(widgetIndex, name, input.value);
        else sendTransformUpdate(widgetIndex, name, input.value);
    }
    container.appendChild(input);
    return container;
}

// Layout Menu
function loadLayout() {
    const filePicker = document.createElement("input");
    filePicker.type = "file";
    filePicker.accept = ".mmw";
    filePicker.onchange = e => {
        console.log(e.target.files[0]);
    };
    filePicker.click();
}

// Setup
fetchInitial();