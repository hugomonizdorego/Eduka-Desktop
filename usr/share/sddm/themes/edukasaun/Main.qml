// Edukasaun OS login screen for SDDM (0.9.16).
// Plain QtQuick items only, so it runs on the Qt 5 and the Qt 6 greeter.
// Settings (theme.conf, overridden by theme.conf.user written by
// Eduka-Settings → Login Screen):
//   style=light|dark|glass  accent=#rrggbb  title=…  showClock=true|false
//   background=/usr/share/Edukasaun/SDDM/Default.png  logo=…  defaultUser=…

import QtQuick 2.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1366
    height: 768
    color: "#1f6b45"

    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property string style: ["light", "dark", "glass"].indexOf(String(config.style)) >= 0 ? String(config.style) : "light"
    property bool dark: style === "dark"
    property bool glass: style === "glass"
    property color accent: /^#[0-9a-fA-F]{6}$/.test(String(config.accent)) ? String(config.accent) : (dark ? "#26a69a" : (glass ? "#1e9bd7" : "#00a879"))
    property bool showClock: String(config.showClock) !== "false"
    property bool busy: false
    property string timeText: ""
    // Accounts SDDM lists (hidden ones, like the locked live account on an
    // installed computer, are not in userModel).
    property var knownUsers: []

    Repeater {
        model: userModel
        delegate: Item { Component.onCompleted: root.knownUsers = root.knownUsers.concat([model.name]) }
    }

    function initialUser() {
        var last = userModel.lastUser ? String(userModel.lastUser) : ""
        var wanted = config.defaultUser ? String(config.defaultUser) : ""
        if (last.length > 0 && knownUsers.indexOf(last) >= 0) return last
        if (wanted.length > 0 && knownUsers.indexOf(wanted) >= 0) return wanted
        if (knownUsers.length === 1) return knownUsers[0]
        return last.length > 0 && knownUsers.length === 0 ? last : ""
    }

    function setupUser() {
        if (user.text.length === 0) user.text = initialUser()
        if (user.text.length > 0) password.forceActiveFocus()
        else user.forceActiveFocus()
    }
    property real s: Math.max(0.75, Math.min(1.25, height / 768))

    // Colors of each style.
    property color cardColor: dark ? "#eb262626" : (glass ? "#8cffffff" : "#f5ffffff")
    property color cardBorder: dark ? "#33ffffff" : (glass ? "#e6ffffff" : "#ccffffff")
    property color fieldColor: dark ? "#383838" : (glass ? "#d9ffffff" : "#ffffff")
    property color fieldBorder: dark ? "#40ffffff" : (glass ? "#f2ffffff" : "#d3e0db")
    property color textColor: dark ? "#ffffff" : "#10231e"
    property color subColor: dark ? "#a6ffffff" : "#5b6e69"
    property color hintColor: dark ? "#73ffffff" : "#8aa29b"

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
            shake.start()
            password.forceActiveFocus()
        }
        function onInformationMessage(text) {
            message.text = text
        }
    }

    function doLogin() {
        if (busy) return
        if (user.text.length === 0) { user.forceActiveFocus(); return }
        message.text = ""
        busy = true
        sddm.login(user.text, password.text, root.sessionIndex)
    }

    // Built-in background when the picture is missing.
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: root.dark ? "#2f3b39" : (root.glass ? "#bfe3f5" : "#e9f6c9") }
            GradientStop { position: 0.5; color: root.dark ? "#1f2a28" : (root.glass ? "#7fb9dc" : "#8fcf7a") }
            GradientStop { position: 1.0; color: root.dark ? "#121616" : (root.glass ? "#2f6f9a" : "#1f6b45") }
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

    // Veil: darkens the picture for the dark style, softens it for glass.
    Rectangle {
        anchors.fill: parent
        color: root.dark ? "#8c000000" : (root.glass ? "#26ffffff" : "#14000000")
    }

    // Clock and date above the card.
    Column {
        id: clock
        visible: root.showClock
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: card.top
        anchors.bottomMargin: 28 * root.s
        spacing: 0
        Text {
            id: clockTime
            anchors.horizontalCenter: parent.horizontalCenter
            color: "white"; font.pixelSize: 64 * root.s; font.weight: Font.Light
            style: Text.Raised; styleColor: "#33000000"
        }
        Text {
            id: clockDate
            anchors.horizontalCenter: parent.horizontalCenter
            color: "white"; font.pixelSize: 18 * root.s; font.weight: Font.DemiBold
            style: Text.Raised; styleColor: "#33000000"
        }
        Timer {
            interval: 1000; running: true; repeat: true; triggeredOnStart: true
            onTriggered: {
                var now = new Date()
                root.timeText = Qt.formatTime(now, "HH:mm")
                clockTime.text = root.timeText
                clockDate.text = Qt.formatDate(now, "dddd, d MMMM yyyy")
            }
        }
    }

    // Login card.
    Rectangle {
        id: card
        width: 380 * root.s
        height: column.implicitHeight + 52 * root.s
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: root.showClock ? 50 * root.s : 0
        radius: 28 * root.s
        color: root.cardColor
        border.color: root.cardBorder
        border.width: 1

        // Thin highlight along the top edge (glass rim).
        Rectangle {
            visible: root.glass
            anchors.top: parent.top; anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 1
            width: parent.width - 2 * parent.radius; height: 1
            color: "#ffffff"
        }

        SequentialAnimation {
            id: shake
            NumberAnimation { target: card; property: "anchors.horizontalCenterOffset"; to: -10; duration: 50 }
            NumberAnimation { target: card; property: "anchors.horizontalCenterOffset"; to: 10; duration: 70 }
            NumberAnimation { target: card; property: "anchors.horizontalCenterOffset"; to: -6; duration: 60 }
            NumberAnimation { target: card; property: "anchors.horizontalCenterOffset"; to: 0; duration: 50 }
        }

        Column {
            id: column
            anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
            anchors.margins: 26 * root.s
            spacing: 12 * root.s

            // Logo with the user's initial as a small badge.
            Item {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 92 * root.s; height: 92 * root.s
                Rectangle {
                    anchors.fill: parent
                    radius: width / 2
                    color: root.dark ? "#1affffff" : "#ffffff"
                    border.color: root.accent; border.width: 2
                }
                Image {
                    id: logo
                    anchors.centerIn: parent
                    width: parent.width * 0.7; height: parent.height * 0.7
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                    source: config.logo ? "file://" + config.logo : "logo.png"
                    onStatusChanged: if (status === Image.Error && source != Qt.resolvedUrl("logo.png")) source = "logo.png"
                }
                Rectangle {
                    visible: user.text.length > 0
                    anchors.right: parent.right; anchors.bottom: parent.bottom
                    width: 30 * root.s; height: width; radius: width / 2
                    color: root.accent
                    border.color: root.dark ? "#262626" : "#ffffff"; border.width: 2
                    Text {
                        anchors.centerIn: parent
                        text: user.text.length > 0 ? user.text.charAt(0).toUpperCase() : ""
                        color: "white"; font.pixelSize: 14 * root.s; font.bold: true
                    }
                }
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: config.title ? config.title : "Edukasaun"
                color: root.textColor; font.pixelSize: 26 * root.s; font.bold: true
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Sign in to Eduka-Desktop"
                color: root.subColor; font.pixelSize: 13 * root.s
            }

            Item { width: 1; height: 2 * root.s }

            // User name
            Rectangle {
                width: parent.width; height: 46 * root.s; radius: height / 2
                color: root.fieldColor
                border.color: user.activeFocus ? root.accent : root.fieldBorder
                border.width: user.activeFocus ? 2 : 1
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left; anchors.leftMargin: 20 * root.s
                    text: "User name"; color: root.hintColor; font.pixelSize: 15 * root.s
                    visible: user.text.length === 0 && !user.activeFocus
                }
                TextInput {
                    id: user
                    anchors.fill: parent; anchors.leftMargin: 20 * root.s; anchors.rightMargin: 20 * root.s
                    verticalAlignment: TextInput.AlignVCenter
                    font.pixelSize: 16 * root.s; color: root.textColor
                    selectionColor: root.accent
                    clip: true
                    KeyNavigation.tab: password
                    Keys.onReturnPressed: password.forceActiveFocus()
                    Keys.onEnterPressed: password.forceActiveFocus()
                }
            }

            // Password with the login arrow inside.
            Rectangle {
                width: parent.width; height: 46 * root.s; radius: height / 2
                color: root.fieldColor
                border.color: password.activeFocus ? root.accent : root.fieldBorder
                border.width: password.activeFocus ? 2 : 1
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left; anchors.leftMargin: 20 * root.s
                    text: "Password"; color: root.hintColor; font.pixelSize: 15 * root.s
                    visible: password.text.length === 0
                }
                TextInput {
                    id: password
                    anchors.left: parent.left; anchors.right: go.left
                    anchors.top: parent.top; anchors.bottom: parent.bottom
                    anchors.leftMargin: 20 * root.s; anchors.rightMargin: 8 * root.s
                    verticalAlignment: TextInput.AlignVCenter
                    font.pixelSize: 16 * root.s; color: root.textColor
                    selectionColor: root.accent
                    echoMode: TextInput.Password
                    passwordCharacter: "●"
                    clip: true
                    focus: true
                    KeyNavigation.backtab: user
                    Keys.onReturnPressed: root.doLogin()
                    Keys.onEnterPressed: root.doLogin()
                }
                Rectangle {
                    id: go
                    anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                    anchors.rightMargin: 5 * root.s
                    width: parent.height - 10 * root.s; height: width; radius: width / 2
                    color: goArea.pressed ? Qt.darker(root.accent, 1.15) : (goArea.containsMouse ? Qt.lighter(root.accent, 1.12) : root.accent)
                    Canvas {
                        id: arrow
                        anchors.centerIn: parent
                        width: parent.width * 0.5; height: width
                        visible: !root.busy
                        onPaint: {
                            var c = getContext("2d"); c.reset()
                            c.strokeStyle = "white"; c.lineWidth = width * 0.12; c.lineCap = "round"; c.lineJoin = "round"
                            c.beginPath(); c.moveTo(width * 0.15, height * 0.5); c.lineTo(width * 0.85, height * 0.5)
                            c.moveTo(width * 0.55, height * 0.2); c.lineTo(width * 0.85, height * 0.5); c.lineTo(width * 0.55, height * 0.8)
                            c.stroke()
                        }
                    }
                    Text {
                        anchors.centerIn: parent; visible: root.busy
                        text: "…"; color: "white"; font.pixelSize: 18 * root.s; font.bold: true
                    }
                    MouseArea {
                        id: goArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.doLogin()
                    }
                }
            }

            Text {
                id: capsLock
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: "Caps Lock is on"
                color: root.dark ? "#ffe082" : "#8a5a00"; font.pixelSize: 12 * root.s
                visible: typeof keyboard !== "undefined" && keyboard.capsLock && password.activeFocus
            }

            Text {
                id: message
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                color: root.dark ? "#ef9a9a" : "#b3261e"; font.pixelSize: 13 * root.s
                visible: text.length > 0
            }
        }
    }

    // Bottom bar in the style of Eduka-Panel.
    Rectangle {
        id: bar
        anchors.bottom: parent.bottom; anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 14 * root.s
        width: Math.min(parent.width - 28, Math.max(560 * root.s, parent.width * 0.6))
        height: 50 * root.s; radius: height / 2
        color: root.dark ? "#d9262626" : (root.glass ? "#80ffffff" : "#e6ffffff")
        border.color: root.cardBorder; border.width: 1

        Row {
            anchors.left: parent.left; anchors.leftMargin: 8 * root.s
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10 * root.s
            Rectangle {
                width: label.implicitWidth + 28 * root.s; height: 36 * root.s; radius: height / 2
                color: root.accent
                Text {
                    id: label
                    anchors.centerIn: parent
                    text: config.title ? config.title : "Edukasaun"
                    color: "white"; font.pixelSize: 14 * root.s; font.bold: true
                }
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: "Eduka-Desktop"
                color: root.subColor; font.pixelSize: 13 * root.s; font.bold: true
            }
        }

        Row {
            anchors.right: parent.right; anchors.rightMargin: 8 * root.s
            anchors.verticalCenter: parent.verticalCenter
            spacing: 6 * root.s

            Text {
                anchors.verticalCenter: parent.verticalCenter
                visible: !root.showClock
                text: root.timeText
                color: root.textColor; font.pixelSize: 14 * root.s; font.bold: true
                rightPadding: 8 * root.s
            }

            Repeater {
                model: [
                    { label: "Restart", action: "reboot", show: sddm.canReboot },
                    { label: "Shut Down", action: "poweroff", show: sddm.canPowerOff }
                ]
                delegate: Rectangle {
                    visible: modelData.show
                    width: 36 * root.s; height: width; radius: width / 2
                    color: area.containsMouse ? (modelData.action === "poweroff" ? "#e5484d" : root.accent) : "transparent"
                    Canvas {
                        id: icon
                        anchors.centerIn: parent
                        width: parent.width * 0.5; height: width
                        property color ink: area.containsMouse ? "white" : root.textColor
                        onInkChanged: requestPaint()
                        onPaint: {
                            var c = getContext("2d"); c.reset()
                            c.strokeStyle = ink; c.fillStyle = ink; c.lineWidth = width * 0.11; c.lineCap = "round"
                            var r = width * 0.4, cx = width / 2, cy = height / 2 + width * 0.04
                            c.beginPath()
                            if (modelData.action === "poweroff") {
                                c.arc(cx, cy, r, -Math.PI / 2 + 0.75, 3 * Math.PI / 2 - 0.75, false)
                                c.moveTo(cx, cy - r - width * 0.06); c.lineTo(cx, cy - width * 0.05)
                                c.stroke()
                            } else {
                                c.arc(cx, cy, r, -Math.PI / 2, Math.PI * 1.15, false)
                                c.stroke()
                                c.beginPath()
                                c.moveTo(cx, cy - r - width * 0.14); c.lineTo(cx + width * 0.2, cy - r); c.lineTo(cx, cy - r + width * 0.14)
                                c.closePath(); c.fill()
                            }
                        }
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
    }

    Component.onCompleted: Qt.callLater(setupUser)
}
