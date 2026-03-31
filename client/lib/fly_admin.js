// Flyton Inline Editor
// Generic inline editing module for any HTML element with flyton-admin attribute
// (c) KICDEV 2025

function initFlytonEditor() {
        // Check if global flag exists
        if (!fly_edit_mode) {
            console.log("Not an admin, editor disabled");
            return;
        }

        let items = document.querySelectorAll('[flyton-admin]');
        for (const item of items) {
            let originalText = item.innerText;
            let flytonKey = item.getAttribute("flyton-admin");

            // Avoid duplicate button
            if (item.querySelector('.flyton-edit-button')) continue;

            let editButton = document.createElement("button");
            editButton.textContent = "[Edit]";
            editButton.className = "flyton-edit-button";
            editButton.style.marginLeft = "10px";

            editButton.onclick = function() {
                openInlineEditor(item, originalText, flytonKey);
            };

            item.appendChild(editButton);
        }
    }
    // Create inline editor for specific element
function openInlineEditor(item, originalText, flytonKey) {
        item.innerHTML = "";

        let inputField = document.createElement("input");
        inputField.type = "text";
        inputField.value = originalText;
        inputField.style.width = "60%";

        let saveButton = document.createElement("button");
        saveButton.textContent = "Save";
        saveButton.onclick = function() {
            saveFlytonChange(flytonKey, inputField.value, item);
        };

        let cancelButton = document.createElement("button");
        cancelButton.textContent = "X";
        cancelButton.onclick = function() {
            cancelInlineEdit(item, originalText);
        };



        item.appendChild(inputField);
        item.appendChild(saveButton);
        item.appendChild(cancelButton);
    }

    // Restore original text after cancel
function cancelInlineEdit(item, originalText) {
        item.innerText = originalText;
        initFlytonEditor();
    }

    // Save change to server using existing call_server function
async function saveFlytonChange(flytonKey, newValue, item) {
    console.log("Saving:", flytonKey, newValue);

    let inp = {
        flyton: flytonKey,
        value: newValue
    };

    let res = await call_server("api_fly_admin", inp);
    console.log(res);
    if (res.server.allow) {
        item.innerText = newValue;
        window.location.href = window.location.href;



    } else {
        alert(res.server ? res.server.err : "Unknown server error");
    }
}

