// Edukasaun OS login screen for SDDM.
// Plain QtQuick items only, so it runs on the Qt 5 and the Qt 6 greeter.
// Background: /usr/share/Edukasaun/SDDM/Default.png (see theme.conf).

import QtQuick 2.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1366
    height: 768
    color: "#1f6b45"

    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property string accent: "#00a879"
    property bool busy: false

    TextConstants { id: textConstants }

    Connections {
        target: sddm
        function onLoginSucceeded() {
            root.busy = false
        }
        function onLoginFailed() {
            root.busy = false
            password.text = ""
            message.text = "Wrong user name or password. Please try again."
            password.forceActiveFocus()
        }
        function onInformationMessage(text) {
            message.text = text
        }
    }

    function doLogin() {
        if (busy) return
        message.text = ""
        busy = true
        sddm.login(user.text, password.text, root.sessionIndex)
    }

    // Fallback when the background image is missing: soft Edukasaun green.
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#f2f7c6" }
            GradientStop { position: 0.45; color: "#a9d673" }
            GradientStop { position: 0.8; color: "#3f8f55" }
            GradientStop { position: 1.0; color: "#1f6b45" }
        }
    }

    Image {
        id: background
        anchors.fill: parent
        source: config.background ? "file://" + config.background : ""
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        visible: status === Image.Ready
        smooth: true
    }

    // Light veil at the bottom so the power buttons stay readable.
    Rectangle {
        anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
        height: 120
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#00000000" }
            GradientStop { position: 1.0; color: "#55000000" }
        }
    }

    // Clock, top right.
    Column {
        anchors.top: parent.top; anchors.right: parent.right
        anchors.margins: 36
        spacing: 2
        Text {
            id: clockTime
            anchors.right: parent.right
            color: "white"; font.pixelSize: 54; font.weight: Font.DemiBold
            style: Text.Raised; styleColor: "#40000000"
        }
        Text {
            id: clockDate
            anchors.right: parent.right
            color: "white"; font.pixelSize: 18
            style: Text.Raised; styleColor: "#40000000"
        }
        Timer {
            interval: 1000; running: true; repeat: true; triggeredOnStart: true
            onTriggered: {
                var now = new Date()
                clockTime.text = Qt.formatTime(now, "HH:mm")
                clockDate.text = Qt.formatDate(now, "dddd, d MMMM yyyy")
            }
        }
    }

    // Login card.
    Rectangle {
        id: card
        width: 400
        height: column.implicitHeight + 56
        anchors.centerIn: parent
        radius: 26
        color: "#e6ffffff"
        border.color: "#ccffffff"
        border.width: 1

        Column {
            id: column
            anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
            anchors.margins: 28
            spacing: 14

            Image {
                id: logo
                anchors.horizontalCenter: parent.horizontalCenter
                width: 84; height: 84
                fillMode: Image.PreserveAspectFit
                smooth: true
                source: config.logo ? "file://" + config.logo : "logo.png"
                onStatusChanged: if (status === Image.Error && source != Qt.resolvedUrl("logo.png")) source = "logo.png"
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: config.title ? config.title : "Edukasaun"
                color: "#10231e"; font.pixelSize: 28; font.bold: true
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Eduka-Desktop"
                color: "#536a64"; font.pixelSize: 14
            }

            Item { width: 1; height: 4 }

            // User name
            Rectangle {
                width: parent.width; height: 46; radius: 23
                color: "white"
                border.color: user.activeFocus ? root.accent : "#cfe3dc"
                border.width: user.activeFocus ? 2 : 1
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left; anchors.leftMargin: 20
                    text: "User name"; color: "#8aa29b"; font.pixelSize: 15
                    visible: user.text.length === 0 && !user.activeFocus
                }
                TextInput {
                    id: user
                    anchors.fill: parent; anchors.leftMargin: 20; anchors.rightMargin: 20
                    verticalAlignment: TextInput.AlignVCenter
                    font.pixelSize: 16; color: "#10231e"
                    clip: true
                    text: userModel.lastUser ? userModel.lastUser : (config.defaultUser ? config.defaultUser : "")
                    KeyNavigation.tab: password
                    Keys.onReturnPressed: password.forceActiveFocus()
                    Keys.onEnterPressed: password.forceActiveFocus()
                }
            }

            // Password
            Rectangle {
                width: parent.width; height: 46; radius: 23
                color: "white"
                border.color: password.activeFocus ? root.accent : "#cfe3dc"
                border.width: password.activeFocus ? 2 : 1
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left; anchors.leftMargin: 20
                    text: "Password"; color: "#8aa29b"; font.pixelSize: 15
                    visible: password.text.length === 0
                }
                TextInput {
                    id: password
                    anchors.fill: parent; anchors.leftMargin: 20; anchors.rightMargin: 20
                    verticalAlignment: TextInput.AlignVCenter
                    font.pixelSize: 16; color: "#10231e"
                    echoMode: TextInput.Password
                    passwordCharacter: "●"
                    clip: true
                    focus: true
                    KeyNavigation.backtab: user
                    Keys.onReturnPressed: root.doLogin()
                    Keys.onEnterPressed: root.doLogin()
                }
            }

            // Log in button
            Rectangle {
                width: parent.width; height: 46; radius: 23
                color: loginArea.pressed ? "#00946b" : (loginArea.containsMouse ? "#00b683" : root.accent)
                Text {
                    anchors.centerIn: parent
                    text: root.busy ? "Logging in…" : "Log In"
                    color: "white"; font.pixelSize: 16; font.bold: true
                }
                MouseArea {
                    id: loginArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.doLogin()
                }
            }

            Text {
                id: message
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                color: "#b3261e"; font.pixelSize: 13
                visible: text.length > 0
            }
        }
    }

    // Power buttons, bottom right.
    Row {
        anchors.right: parent.right; anchors.bottom: parent.bottom
        anchors.margins: 28
        spacing: 12

        Repeater {
            model: [
                { label: "Restart", action: "reboot", show: sddm.canReboot },
                { label: "Shut Down", action: "poweroff", show: sddm.canPowerOff }
            ]
            delegate: Rectangle {
                visible: modelData.show
                width: label.implicitWidth + 36; height: 40; radius: 20
                color: area.containsMouse ? "#40ffffff" : "#26ffffff"
                border.color: "#66ffffff"; border.width: 1
                Text {
                    id: label
                    anchors.centerIn: parent
                    text: modelData.label
                    color: "white"; font.pixelSize: 14; font.bold: true
                }
                MouseArea {
                    id: area
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: modelData.action === "reboot" ? sddm.reboot() : sddm.powerOff()
                }
            }
        }
    }

    // Session name, bottom left (Eduka-Desktop is the only session).
    Text {
        anchors.left: parent.left; anchors.bottom: parent.bottom
        anchors.margins: 32
        text: "Edukasaun OS  •  Eduka-Desktop"
        color: "white"; font.pixelSize: 14; font.bold: true
        style: Text.Raised; styleColor: "#40000000"
    }

    Component.onCompleted: {
        if (user.text.length > 0) password.forceActiveFocus()
        else user.forceActiveFocus()
    }
}
