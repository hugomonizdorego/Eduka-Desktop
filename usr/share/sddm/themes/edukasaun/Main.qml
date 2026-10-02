// Edukasaun OS login screen for SDDM (0.9.19).
// Plain QtQuick items only, so it runs on the Qt 5 and the Qt 6 greeter.
//
// Settings (theme.conf, overridden by theme.conf.user written by
// Eduka-Settings → Login Screen):
//   style=light|dark|glass  accent=#rrggbb  title=…  showClock=true|false
//   background=/usr/share/Edukasaun/SDDM/Default.png  logo=…  defaultUser=…
//
// Bottom bar: session, keyboard layout and language on the left;
// accessibility (larger text, high contrast, on-screen keyboard) and power
// (suspend, restart, shut down) on the right.
//
// The language chosen here is used by this screen and, when the greeter may
// write files (QML_XHR_ALLOW_FILE_WRITE, set in /etc/sddm.conf.d/10-edukasaun.conf),
// by the Eduka-Desktop session after login: the greeter writes the user name
// and the language to /var/lib/edukasaun-desktop/login/language and
// eduka-desktop-session checks both before it uses them.

import QtQuick 2.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1366
    height: 768
    color: "#1f6b45"

    // ------------------------------------------------------------ settings
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property string style: ["light", "dark", "glass"].indexOf(String(config.style)) >= 0 ? String(config.style) : "light"
    property bool contrast: false
    property bool largeText: false
    property bool dark: style === "dark"
    property bool glass: style === "glass"
    property color accent: contrast ? "#ffd400" : (/^#[0-9a-fA-F]{6}$/.test(String(config.accent)) ? String(config.accent) : (dark ? "#26a69a" : (glass ? "#1e9bd7" : "#00a879")))
    property bool showClock: String(config.showClock) !== "false"
    property bool busy: false
    property bool menuOpen: menus.open !== ""
    property real s: Math.max(0.75, Math.min(1.25, height / 768)) * (largeText ? 1.25 : 1.0)

    property color cardColor: contrast ? "#000000" : (dark ? "#e6202322" : (glass ? "#8cffffff" : "#f2ffffff"))
    property color cardBorder: contrast ? "#ffffff" : (dark ? "#33ffffff" : (glass ? "#e6ffffff" : "#d9ffffff"))
    property color fieldColor: contrast ? "#000000" : (dark ? "#2e3432" : (glass ? "#d9ffffff" : "#ffffff"))
    property color fieldBorder: contrast ? "#ffffff" : (dark ? "#40ffffff" : (glass ? "#f2ffffff" : "#d3e0db"))
    property color textColor: contrast ? "#ffffff" : (dark ? "#ffffff" : "#10231e")
    property color subColor: contrast ? "#ffffff" : (dark ? "#b3ffffff" : "#5b6e69")
    property color hintColor: contrast ? "#d9ffffff" : (dark ? "#80ffffff" : "#8aa29b")
    property color barColor: contrast ? "#000000" : (dark ? "#d9202322" : (glass ? "#80ffffff" : "#e6ffffff"))
    property color hoverColor: contrast ? "#333333" : (dark ? "#1affffff" : "#1a00785a")

    // ------------------------------------------------------------ language
    // Language of this screen: the one picked in the menu, else the system's.
    property string language: ""
    property string lang: language.length > 0 ? language : String(Qt.locale().name)
    readonly property var languages: [
        { code: "", name: "System language" },
        { code: "en_US", name: "English" },
        { code: "pt_PT", name: "Português (Portugal)" },
        { code: "pt_BR", name: "Português (Brasil)" },
        { code: "tet", name: "Tetun" },
        { code: "id_ID", name: "Bahasa Indonesia" },
        { code: "ms_MY", name: "Bahasa Melayu" },
        { code: "tl_PH", name: "Filipino" },
        { code: "th_TH", name: "ไทย" },
        { code: "vi_VN", name: "Tiếng Việt" },
        { code: "zh_CN", name: "简体中文" },
        { code: "zh_TW", name: "繁體中文" }
    ]
    readonly property var strings: ({
        pt: { "Sign in to Eduka-Desktop": "Entrar no Eduka-Desktop", "User name": "Nome de utilizador", "Password": "Palavra-passe",
              "Other user…": "Outro utilizador…", "Back": "Voltar", "Caps Lock is on": "Caps Lock está ativo",
              "Wrong user name or password. Please try again.": "Nome de utilizador ou palavra-passe errados. Tente novamente.",
              "Signing in…": "A entrar…", "Language": "Idioma", "System language": "Idioma do sistema", "Keyboard": "Teclado",
              "Accessibility": "Acessibilidade", "Larger text": "Texto maior", "High contrast": "Alto contraste",
              "On-screen keyboard": "Teclado no ecrã", "Not installed": "Não instalado", "Power": "Energia",
              "Suspend": "Suspender", "Hibernate": "Hibernar", "Restart": "Reiniciar", "Shut Down": "Desligar",
              "Session": "Sessão", "Used on this screen and on the desktop after you sign in.": "Usado neste ecrã e no ambiente de trabalho depois de entrar." },
        pt_BR: { "User name": "Nome de usuário", "Password": "Senha", "Other user…": "Outro usuário…",
              "Wrong user name or password. Please try again.": "Nome de usuário ou senha incorretos. Tente novamente.",
              "Signing in…": "Entrando…", "On-screen keyboard": "Teclado na tela",
              "Used on this screen and on the desktop after you sign in.": "Usado nesta tela e na área de trabalho depois de entrar." },
        tet: { "Sign in to Eduka-Desktop": "Tama ba Eduka-Desktop", "User name": "Naran uza-na'in", "Password": "Liafuan-xave",
              "Other user…": "Uza-na'in seluk…", "Back": "Fila", "Caps Lock is on": "Caps Lock moris",
              "Wrong user name or password. Please try again.": "Naran ka liafuan-xave sala. Koko fali.",
              "Signing in…": "Tama hela…", "Language": "Lian", "System language": "Lian sistema", "Keyboard": "Tekladu",
              "Accessibility": "Asesibilidade", "Larger text": "Testu boot liu", "High contrast": "Kontraste aas",
              "On-screen keyboard": "Tekladu iha ekran", "Not installed": "La instala", "Power": "Enerjia",
              "Suspend": "Suspende", "Hibernate": "Iberna", "Restart": "Hahú fali", "Shut Down": "Hamate",
              "Session": "Sesaun", "Used on this screen and on the desktop after you sign in.": "Uza iha ekran ida-ne'e no iha desktop hafoin tama." },
        id: { "Sign in to Eduka-Desktop": "Masuk ke Eduka-Desktop", "User name": "Nama pengguna", "Password": "Kata sandi",
              "Other user…": "Pengguna lain…", "Back": "Kembali", "Caps Lock is on": "Caps Lock aktif",
              "Wrong user name or password. Please try again.": "Nama pengguna atau kata sandi salah. Coba lagi.",
              "Signing in…": "Sedang masuk…", "Language": "Bahasa", "System language": "Bahasa sistem", "Keyboard": "Papan ketik",
              "Accessibility": "Aksesibilitas", "Larger text": "Teks lebih besar", "High contrast": "Kontras tinggi",
              "On-screen keyboard": "Papan ketik layar", "Not installed": "Belum terpasang", "Power": "Daya",
              "Suspend": "Tidur", "Hibernate": "Hibernasi", "Restart": "Mulai Ulang", "Shut Down": "Matikan",
              "Session": "Sesi", "Used on this screen and on the desktop after you sign in.": "Dipakai di layar ini dan di desktop setelah masuk." },
        ms: { "Sign in to Eduka-Desktop": "Log masuk ke Eduka-Desktop", "User name": "Nama pengguna", "Password": "Kata laluan",
              "Other user…": "Pengguna lain…", "Back": "Kembali", "Caps Lock is on": "Caps Lock dihidupkan",
              "Wrong user name or password. Please try again.": "Nama pengguna atau kata laluan salah. Cuba lagi.",
              "Signing in…": "Sedang log masuk…", "Language": "Bahasa", "System language": "Bahasa sistem", "Keyboard": "Papan kekunci",
              "Accessibility": "Kebolehcapaian", "Larger text": "Teks lebih besar", "High contrast": "Kontras tinggi",
              "On-screen keyboard": "Papan kekunci skrin", "Not installed": "Tidak dipasang", "Power": "Kuasa",
              "Suspend": "Tangguh", "Hibernate": "Hibernasi", "Restart": "Mula Semula", "Shut Down": "Matikan",
              "Session": "Sesi", "Used on this screen and on the desktop after you sign in.": "Digunakan pada skrin ini dan pada desktop selepas log masuk." },
        tl: { "Sign in to Eduka-Desktop": "Mag-sign in sa Eduka-Desktop", "User name": "Pangalan ng user", "Password": "Password",
              "Other user…": "Ibang user…", "Back": "Bumalik", "Caps Lock is on": "Naka-on ang Caps Lock",
              "Wrong user name or password. Please try again.": "Mali ang pangalan o password. Subukan muli.",
              "Signing in…": "Nagsa-sign in…", "Language": "Wika", "System language": "Wika ng system", "Keyboard": "Keyboard",
              "Accessibility": "Accessibility", "Larger text": "Mas malaking teksto", "High contrast": "Mataas na contrast",
              "On-screen keyboard": "On-screen keyboard", "Not installed": "Hindi naka-install", "Power": "Power",
              "Suspend": "I-suspend", "Hibernate": "I-hibernate", "Restart": "I-restart", "Shut Down": "I-shut Down",
              "Session": "Session", "Used on this screen and on the desktop after you sign in.": "Gagamitin dito at sa desktop pagkatapos mag-sign in." },
        th: { "Sign in to Eduka-Desktop": "เข้าสู่ระบบ Eduka-Desktop", "User name": "ชื่อผู้ใช้", "Password": "รหัสผ่าน",
              "Other user…": "ผู้ใช้อื่น…", "Back": "ย้อนกลับ", "Caps Lock is on": "Caps Lock เปิดอยู่",
              "Wrong user name or password. Please try again.": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง",
              "Signing in…": "กำลังเข้าสู่ระบบ…", "Language": "ภาษา", "System language": "ภาษาของระบบ", "Keyboard": "แป้นพิมพ์",
              "Accessibility": "การช่วยการเข้าถึง", "Larger text": "ตัวอักษรใหญ่ขึ้น", "High contrast": "คอนทราสต์สูง",
              "On-screen keyboard": "แป้นพิมพ์บนหน้าจอ", "Not installed": "ไม่ได้ติดตั้ง", "Power": "พลังงาน",
              "Suspend": "พักเครื่อง", "Hibernate": "ไฮเบอร์เนต", "Restart": "เริ่มใหม่", "Shut Down": "ปิดเครื่อง",
              "Session": "เซสชัน", "Used on this screen and on the desktop after you sign in.": "ใช้กับหน้าจอนี้และเดสก์ท็อปหลังเข้าสู่ระบบ" },
        vi: { "Sign in to Eduka-Desktop": "Đăng nhập vào Eduka-Desktop", "User name": "Tên người dùng", "Password": "Mật khẩu",
              "Other user…": "Người dùng khác…", "Back": "Quay lại", "Caps Lock is on": "Caps Lock đang bật",
              "Wrong user name or password. Please try again.": "Sai tên người dùng hoặc mật khẩu. Vui lòng thử lại.",
              "Signing in…": "Đang đăng nhập…", "Language": "Ngôn ngữ", "System language": "Ngôn ngữ hệ thống", "Keyboard": "Bàn phím",
              "Accessibility": "Trợ năng", "Larger text": "Chữ lớn hơn", "High contrast": "Độ tương phản cao",
              "On-screen keyboard": "Bàn phím ảo", "Not installed": "Chưa cài đặt", "Power": "Nguồn",
              "Suspend": "Tạm ngưng", "Hibernate": "Ngủ đông", "Restart": "Khởi động lại", "Shut Down": "Tắt máy",
              "Session": "Phiên", "Used on this screen and on the desktop after you sign in.": "Dùng cho màn hình này và màn hình nền sau khi đăng nhập." },
        zh_CN: { "Sign in to Eduka-Desktop": "登录 Eduka-Desktop", "User name": "用户名", "Password": "密码",
              "Other user…": "其他用户…", "Back": "返回", "Caps Lock is on": "大写锁定已打开",
              "Wrong user name or password. Please try again.": "用户名或密码错误，请重试。",
              "Signing in…": "正在登录…", "Language": "语言", "System language": "系统语言", "Keyboard": "键盘",
              "Accessibility": "无障碍", "Larger text": "大号文字", "High contrast": "高对比度",
              "On-screen keyboard": "屏幕键盘", "Not installed": "未安装", "Power": "电源",
              "Suspend": "挂起", "Hibernate": "休眠", "Restart": "重新启动", "Shut Down": "关机",
              "Session": "会话", "Used on this screen and on the desktop after you sign in.": "用于此屏幕以及登录后的桌面。" },
        zh_TW: { "Sign in to Eduka-Desktop": "登入 Eduka-Desktop", "User name": "使用者名稱", "Password": "密碼",
              "Other user…": "其他使用者…", "Back": "返回", "Caps Lock is on": "大寫鎖定已開啟",
              "Wrong user name or password. Please try again.": "使用者名稱或密碼錯誤，請再試一次。",
              "Signing in…": "正在登入…", "Language": "語言", "System language": "系統語言", "Keyboard": "鍵盤",
              "Accessibility": "無障礙", "Larger text": "較大文字", "High contrast": "高對比",
              "On-screen keyboard": "螢幕鍵盤", "Not installed": "未安裝", "Power": "電源",
              "Suspend": "暫停", "Hibernate": "休眠", "Restart": "重新啟動", "Shut Down": "關機",
              "Session": "工作階段", "Used on this screen and on the desktop after you sign in.": "用於此畫面以及登入後的桌面。" }
    })

    function tr(text) {
        var l = root.lang.split(".")[0].split("@")[0]
        var base = l.split("_")[0]
        var full = strings[l]
        if (full && full[text] !== undefined) return full[text]
        if (l.indexOf("zh") === 0 && strings[l] === undefined) {
            var zh = (l === "zh_HK" || l === "zh_MO") ? strings["zh_TW"] : strings["zh_CN"]
            if (zh[text] !== undefined) return zh[text]
        }
        var b = strings[base]
        if (b && b[text] !== undefined) return b[text]
        if (base === "tet" && strings["pt"][text] !== undefined) return strings["pt"][text]
        return text
    }

    // The greeter remembers the language it last wrote (read access needs
    // QML_XHR_ALLOW_FILE_READ; without it the system language is used).
    readonly property string langFile: "file:///var/lib/edukasaun-desktop/login/language"
    function loadLanguage() {
        try {
            var x = new XMLHttpRequest()
            x.onreadystatechange = function() {
                if (x.readyState !== XMLHttpRequest.DONE) return
                var m = /(^|\n)lang=([A-Za-z_]{2,6})/.exec(String(x.responseText))
                if (m && languages.some(function(l) { return l.code === m[2] })) root.language = m[2]
            }
            x.open("GET", langFile); x.send()
        } catch (e) {}
    }
    function saveLanguage(name) {
        try {
            var x = new XMLHttpRequest()
            x.open("PUT", langFile)
            x.send("user=" + name + "\nlang=" + root.language + "\n")
        } catch (e) {}
    }

    // ------------------------------------------------------------ users
    property string userName: ""
    property bool manualUser: false

    function pickInitialUser() {
        var last = userModel.lastUser ? String(userModel.lastUser) : ""
        var wanted = config.defaultUser ? String(config.defaultUser) : ""
        if (users.count === 0) { manualUser = true; userField.text = last; return }
        var idx = userModel.lastIndex
        if ((idx < 0 || idx >= users.count || last.length === 0) && wanted.length > 0) {
            for (var i = 0; i < users.count; i++) {
                var item = users.itemAtIndex(i)
                if (item && item.uname === wanted) { idx = i; break }
            }
        }
        if (idx < 0 || idx >= users.count) idx = 0
        users.currentIndex = idx
        root.userName = users.currentItem ? users.currentItem.uname : ""
    }

    function doLogin() {
        if (busy) return
        var name = manualUser ? userField.text : root.userName
        if (name.length === 0) { userField.forceActiveFocus(); return }
        message.text = ""
        busy = true
        saveLanguage(name)
        sddm.login(name, password.text, root.sessionIndex)
    }

    TextConstants { id: textConstants }

    Connections {
        target: sddm
        function onLoginSucceeded() { root.busy = false }
        function onLoginFailed() {
            root.busy = false
            password.text = ""
            message.text = root.tr("Wrong user name or password. Please try again.")
            shake.start()
            password.forceActiveFocus()
        }
        function onInformationMessage(text) { message.text = text }
    }

    // ------------------------------------------------------------ background
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
        visible: status === Image.Ready && !root.contrast
        smooth: true
    }
    // Soft shade from top to bottom keeps white text readable on any picture.
    Rectangle {
        anchors.fill: parent
        visible: !root.contrast
        gradient: Gradient {
            GradientStop { position: 0.0; color: root.dark ? "#a6000000" : "#4d000000" }
            GradientStop { position: 0.45; color: root.dark ? "#73000000" : "#1a000000" }
            GradientStop { position: 1.0; color: root.dark ? "#b3000000" : "#59000000" }
        }
    }
    Rectangle { anchors.fill: parent; visible: root.contrast; color: "#000000" }

    // Click anywhere outside an open menu closes it.
    MouseArea {
        anchors.fill: parent
        enabled: menus.open !== ""
        onClicked: menus.open = ""
    }

    // ------------------------------------------------------------ clock
    Column {
        id: clock
        visible: root.showClock
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: Math.max(24, parent.height * 0.07)
        spacing: 2 * root.s
        Text {
            id: clockTime
            anchors.horizontalCenter: parent.horizontalCenter
            color: "white"; font.pixelSize: 72 * root.s; font.weight: Font.Light
            style: Text.Raised; styleColor: "#40000000"
        }
        Text {
            id: clockDate
            anchors.horizontalCenter: parent.horizontalCenter
            color: "white"; font.pixelSize: 18 * root.s; font.weight: Font.DemiBold
            style: Text.Raised; styleColor: "#40000000"
        }
        Timer {
            interval: 1000; running: true; repeat: true; triggeredOnStart: true
            onTriggered: {
                var now = new Date()
                var loc = Qt.locale(root.lang.indexOf("tet") === 0 ? "pt_PT" : root.lang)
                clockTime.text = Qt.formatTime(now, "HH:mm")
                clockDate.text = now.toLocaleDateString(loc, "dddd, d MMMM yyyy")
            }
        }
    }

    // ------------------------------------------------------------ login
    Item {
        id: center
        width: Math.min(parent.width - 32, 640 * root.s)
        height: loginColumn.implicitHeight
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: root.showClock ? 40 * root.s : 0

        SequentialAnimation {
            id: shake
            NumberAnimation { target: center; property: "anchors.horizontalCenterOffset"; to: -12; duration: 50 }
            NumberAnimation { target: center; property: "anchors.horizontalCenterOffset"; to: 12; duration: 70 }
            NumberAnimation { target: center; property: "anchors.horizontalCenterOffset"; to: -6; duration: 60 }
            NumberAnimation { target: center; property: "anchors.horizontalCenterOffset"; to: 0; duration: 50 }
        }

        Column {
            id: loginColumn
            width: parent.width
            spacing: 14 * root.s

            // Users: a row of pictures; the chosen one is larger.
            ListView {
                id: users
                visible: !root.manualUser
                anchors.horizontalCenter: parent.horizontalCenter
                width: Math.min(parent.width, Math.max(1, count + (otherVisible ? 1 : 0)) * 116 * root.s)
                height: 150 * root.s
                orientation: ListView.Horizontal
                interactive: contentWidth > width
                clip: true
                spacing: 0
                model: userModel
                property bool otherVisible: true
                highlightFollowsCurrentItem: false
                onCurrentIndexChanged: if (currentItem) { root.userName = currentItem.uname; password.text = ""; password.forceActiveFocus() }
                delegate: Item {
                    id: ud
                    property string uname: model.name
                    property bool current: ListView.isCurrentItem
                    width: 116 * root.s; height: users.height
                    Rectangle {
                        id: ring
                        anchors.horizontalCenter: parent.horizontalCenter
                        y: ud.current ? 4 * root.s : 18 * root.s
                        width: (ud.current ? 96 : 72) * root.s; height: width; radius: width / 2
                        color: root.contrast ? "#000000" : "#ffffff"
                        border.color: ud.current ? root.accent : (root.contrast ? "#ffffff" : "#b3ffffff")
                        border.width: ud.current ? 3 : 1
                        Behavior on width { NumberAnimation { duration: 140 } }
                        Behavior on y { NumberAnimation { duration: 140 } }
                        Text {
                            anchors.centerIn: parent
                            visible: face.status !== Image.Ready
                            text: (model.realName && model.realName.length ? model.realName : model.name).charAt(0).toUpperCase()
                            color: root.accent; font.pixelSize: parent.width * 0.42; font.bold: true
                        }
                        Image {
                            id: face
                            anchors.fill: parent; anchors.margins: 3
                            source: model.icon ? model.icon : ""
                            fillMode: Image.PreserveAspectCrop
                            visible: false
                            asynchronous: true
                        }
                        // Round picture: drawn through a canvas clip (no graphical effects module needed).
                        Canvas {
                            id: round
                            anchors.fill: face
                            property string url: face.status === Image.Ready ? String(face.source) : ""
                            visible: url.length > 0
                            onUrlChanged: if (url.length > 0) { if (isImageLoaded(url)) requestPaint(); else loadImage(url) }
                            onImageLoaded: requestPaint()
                            onWidthChanged: requestPaint()
                            onPaint: {
                                var c = getContext("2d"); c.reset()
                                if (url.length === 0 || !isImageLoaded(url)) return
                                c.save()
                                c.beginPath(); c.arc(width / 2, height / 2, width / 2, 0, Math.PI * 2, false); c.closePath(); c.clip()
                                c.drawImage(url, 0, 0, width, height)
                                c.restore()
                            }
                        }
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: ring.bottom; anchors.topMargin: 8 * root.s
                        width: parent.width - 8; horizontalAlignment: Text.AlignHCenter; elide: Text.ElideRight
                        text: model.realName && model.realName.length ? model.realName : model.name
                        color: "white"; font.pixelSize: (ud.current ? 15 : 13) * root.s; font.bold: ud.current
                        style: Text.Raised; styleColor: "#40000000"
                    }
                    MouseArea {
                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                        onClicked: users.currentIndex = index
                    }
                }
                footer: Item {
                    width: users.otherVisible ? 116 * root.s : 0; height: users.height
                    visible: users.otherVisible
                    Rectangle {
                        id: otherRing
                        anchors.horizontalCenter: parent.horizontalCenter
                        y: 18 * root.s
                        width: 72 * root.s; height: width; radius: width / 2
                        color: otherArea.containsMouse ? "#40ffffff" : "#26ffffff"
                        border.color: root.contrast ? "#ffffff" : "#b3ffffff"; border.width: 1
                        Icon { anchors.centerIn: parent; width: parent.width * 0.4; height: width; name: "plus"; ink: "white" }
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: otherRing.bottom; anchors.topMargin: 8 * root.s
                        width: parent.width - 8; horizontalAlignment: Text.AlignHCenter; elide: Text.ElideRight
                        text: root.tr("Other user…")
                        color: "white"; font.pixelSize: 13 * root.s
                        style: Text.Raised; styleColor: "#40000000"
                    }
                    MouseArea {
                        id: otherArea
                        anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                        onClicked: { root.manualUser = true; userField.text = ""; userField.forceActiveFocus() }
                    }
                }
            }

            // Card with the fields.
            Rectangle {
                id: card
                anchors.horizontalCenter: parent.horizontalCenter
                width: Math.min(parent.width, 380 * root.s)
                height: fields.implicitHeight + 36 * root.s
                radius: 26 * root.s
                color: root.cardColor
                border.color: root.cardBorder; border.width: root.contrast ? 2 : 1

                Column {
                    id: fields
                    anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
                    anchors.margins: 18 * root.s
                    spacing: 10 * root.s

                    // Manual user: logo, a back arrow and the user name field.
                    Item {
                        visible: root.manualUser
                        width: parent.width; height: 64 * root.s
                        Rectangle {
                            visible: users.count > 0
                            anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                            width: 34 * root.s; height: width; radius: width / 2
                            color: backArea.containsMouse ? root.hoverColor : "transparent"
                            border.color: root.fieldBorder; border.width: 1
                            Icon { anchors.centerIn: parent; width: parent.width * 0.5; height: width; name: "back"; ink: root.textColor }
                            MouseArea {
                                id: backArea; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                onClicked: { root.manualUser = false; password.forceActiveFocus() }
                            }
                        }
                        Image {
                            id: logo
                            anchors.centerIn: parent
                            width: 60 * root.s; height: width
                            fillMode: Image.PreserveAspectFit; smooth: true
                            source: config.logo ? "file://" + config.logo : "logo.png"
                            onStatusChanged: if (status === Image.Error && source != Qt.resolvedUrl("logo.png")) source = "logo.png"
                        }
                    }

                    Text {
                        width: parent.width; horizontalAlignment: Text.AlignHCenter
                        text: root.manualUser ? (config.title ? config.title : "Edukasaun") : root.tr("Sign in to Eduka-Desktop")
                        color: root.manualUser ? root.textColor : root.subColor
                        font.pixelSize: (root.manualUser ? 22 : 13) * root.s; font.bold: root.manualUser
                        elide: Text.ElideRight
                    }

                    Rectangle {
                        visible: root.manualUser
                        width: parent.width; height: 46 * root.s; radius: height / 2
                        color: root.fieldColor
                        border.color: userField.activeFocus ? root.accent : root.fieldBorder
                        border.width: userField.activeFocus ? 2 : 1
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left; anchors.leftMargin: 20 * root.s
                            text: root.tr("User name"); color: root.hintColor; font.pixelSize: 15 * root.s
                            visible: userField.text.length === 0
                        }
                        TextInput {
                            id: userField
                            anchors.fill: parent; anchors.leftMargin: 20 * root.s; anchors.rightMargin: 20 * root.s
                            verticalAlignment: TextInput.AlignVCenter
                            font.pixelSize: 16 * root.s; color: root.textColor
                            selectionColor: root.accent; clip: true
                            KeyNavigation.tab: password
                            Keys.onReturnPressed: password.forceActiveFocus()
                            Keys.onEnterPressed: password.forceActiveFocus()
                            Keys.onEscapePressed: if (users.count > 0) { root.manualUser = false; password.forceActiveFocus() }
                        }
                    }

                    Rectangle {
                        width: parent.width; height: 46 * root.s; radius: height / 2
                        color: root.fieldColor
                        border.color: password.activeFocus ? root.accent : root.fieldBorder
                        border.width: password.activeFocus ? 2 : 1
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left; anchors.leftMargin: 20 * root.s
                            text: root.busy ? root.tr("Signing in…") : root.tr("Password")
                            color: root.hintColor; font.pixelSize: 15 * root.s
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
                            echoMode: TextInput.Password; passwordCharacter: "●"
                            clip: true; focus: true
                            KeyNavigation.backtab: userField
                            Keys.onReturnPressed: root.doLogin()
                            Keys.onEnterPressed: root.doLogin()
                            Keys.onLeftPressed: if (text.length === 0 && !root.manualUser && users.currentIndex > 0) users.currentIndex--; else event.accepted = false
                            Keys.onRightPressed: if (text.length === 0 && !root.manualUser && users.currentIndex < users.count - 1) users.currentIndex++; else event.accepted = false
                        }
                        Rectangle {
                            id: go
                            anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                            anchors.rightMargin: 5 * root.s
                            width: parent.height - 10 * root.s; height: width; radius: width / 2
                            color: goArea.pressed ? Qt.darker(root.accent, 1.15) : (goArea.containsMouse ? Qt.lighter(root.accent, 1.12) : root.accent)
                            Icon { anchors.centerIn: parent; width: parent.width * 0.5; height: width; name: "arrow"; ink: root.contrast ? "#000000" : "white"; visible: !root.busy }
                            Text { anchors.centerIn: parent; visible: root.busy; text: "…"; color: "white"; font.pixelSize: 18 * root.s; font.bold: true }
                            MouseArea { id: goArea; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.doLogin() }
                        }
                    }

                    Text {
                        width: parent.width; horizontalAlignment: Text.AlignHCenter
                        text: root.tr("Caps Lock is on")
                        color: root.contrast ? "#ffd400" : (root.dark ? "#ffe082" : "#8a5a00"); font.pixelSize: 12 * root.s
                        visible: typeof keyboard !== "undefined" && keyboard.capsLock
                    }
                    Text {
                        id: message
                        width: parent.width; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
                        color: root.contrast ? "#ff8080" : (root.dark ? "#ef9a9a" : "#b3261e"); font.pixelSize: 13 * root.s
                        visible: text.length > 0
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------ bottom bar
    Item {
        id: menus
        property string open: ""
        anchors.fill: parent
        z: 10

        Rectangle {
            id: bar
            anchors.bottom: parent.bottom; anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 14 * root.s
            width: Math.min(parent.width - 28, Math.max(leftRow.width + rightRow.width + 60 * root.s, parent.width * 0.62))
            height: 50 * root.s; radius: height / 2
            color: root.barColor
            border.color: root.cardBorder; border.width: root.contrast ? 2 : 1

            Row {
                id: leftRow
                anchors.left: parent.left; anchors.leftMargin: 7 * root.s
                anchors.verticalCenter: parent.verticalCenter
                spacing: 6 * root.s

                Rectangle {
                    width: brand.implicitWidth + 28 * root.s; height: 36 * root.s; radius: height / 2
                    color: root.accent
                    Text { id: brand; anchors.centerIn: parent; text: config.title ? config.title : "Edukasaun"; color: root.contrast ? "#000000" : "white"; font.pixelSize: 14 * root.s; font.bold: true }
                }
                BarButton {
                    theme: root
                    icon: "session"
                    id: sessionButton
                    visible: sessionNames.names.length > 0
                    label: sessionNames.names.length > root.sessionIndex ? sessionNames.names[root.sessionIndex] : ""
                    tip: root.tr("Session")
                    onActivated: menus.open = sessionNames.names.length > 1 ? (menus.open === "session" ? "" : "session") : ""
                }
                BarButton {
                    theme: root
                    id: keyButton
                    visible: typeof keyboard !== "undefined" && keyboard.layouts && keyboard.layouts.length > 0
                    icon: "keyboard"
                    label: visible && keyboard.layouts[keyboard.currentLayout] ? String(keyboard.layouts[keyboard.currentLayout].shortName).toUpperCase() : ""
                    tip: root.tr("Keyboard")
                    onActivated: menus.open = menus.open === "keyboard" ? "" : "keyboard"
                }
                BarButton {
                    theme: root
                    id: langButton
                    icon: "globe"
                    label: root.languageName(root.language)
                    tip: root.tr("Language")
                    onActivated: menus.open = menus.open === "language" ? "" : "language"
                }
            }

            Row {
                id: rightRow
                anchors.right: parent.right; anchors.rightMargin: 7 * root.s
                anchors.verticalCenter: parent.verticalCenter
                spacing: 6 * root.s
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    visible: !root.showClock
                    text: clockTime.text
                    color: root.textColor; font.pixelSize: 14 * root.s; font.bold: true
                    rightPadding: 6 * root.s
                }
                BarButton {
                    theme: root
                    icon: "access"; tip: root.tr("Accessibility")
                    active: root.largeText || root.contrast || osk.shown
                    onActivated: menus.open = menus.open === "access" ? "" : "access"
                }
                BarButton {
                    theme: root
                    icon: "power"; tip: root.tr("Power"); danger: true
                    onActivated: menus.open = menus.open === "power" ? "" : "power"
                }
            }
        }

        // Session names (only Eduka-Desktop is normally listed).
        Item {
            id: sessionNames
            property var names: []
            Repeater {
                model: sessionModel
                delegate: Item {
                    Component.onCompleted: {
                        var n = sessionNames.names.slice(); n[index] = model.name; sessionNames.names = n
                    }
                }
            }
        }

        // ---- menus, opened above the bar
        PopupMenu {
            theme: root; bottomY: bar.y
            visible: menus.open === "language"
            anchorX: bar.x + leftRow.x + langButton.x
            title: root.tr("Language")
            note: root.tr("Used on this screen and on the desktop after you sign in.")
            items: root.languages.map(function(l) { return { text: l.code === "" ? root.tr("System language") : l.name, checked: l.code === root.language } })
            onPicked: function(i) { root.language = root.languages[i].code; menus.open = ""; password.forceActiveFocus() }
        }
        PopupMenu {
            theme: root; bottomY: bar.y
            visible: menus.open === "keyboard"
            anchorX: bar.x + leftRow.x + keyButton.x
            title: root.tr("Keyboard")
            items: {
                var m = []
                if (!keyButton.visible) return m
                for (var i = 0; i < keyboard.layouts.length; i++) {
                    var l = keyboard.layouts[i]
                    m.push({ text: l.longName + "  (" + String(l.shortName).toUpperCase() + ")", checked: i === keyboard.currentLayout })
                }
                return m
            }
            onPicked: function(i) { keyboard.currentLayout = i; menus.open = ""; password.forceActiveFocus() }
        }
        PopupMenu {
            theme: root; bottomY: bar.y
            visible: menus.open === "session"
            anchorX: bar.x + leftRow.x + sessionButton.x
            title: root.tr("Session")
            items: sessionNames.names.map(function(n, i) { return { text: n, checked: i === root.sessionIndex } })
            onPicked: function(i) { root.sessionIndex = i; menus.open = ""; password.forceActiveFocus() }
        }
        PopupMenu {
            theme: root; bottomY: bar.y
            visible: menus.open === "access"
            anchorX: bar.x + rightRow.x + rightRow.width - width
            title: root.tr("Accessibility")
            items: [
                { text: root.tr("Larger text"), checked: root.largeText },
                { text: root.tr("High contrast"), checked: root.contrast },
                { text: root.tr("On-screen keyboard") + (osk.available ? "" : " — " + root.tr("Not installed")), checked: osk.shown, enabled: osk.available }
            ]
            onPicked: function(i) {
                if (i === 0) root.largeText = !root.largeText
                else if (i === 1) root.contrast = !root.contrast
                else { osk.shown = !osk.shown; menus.open = "" }
                password.forceActiveFocus()
            }
        }
        PopupMenu {
            id: powerMenu
            theme: root; bottomY: bar.y
            visible: menus.open === "power"
            anchorX: bar.x + rightRow.x + rightRow.width - width
            title: root.tr("Power")
            property var actions: {
                var m = []
                if (sddm.canSuspend) m.push({ key: "suspend", icon: "suspend", text: root.tr("Suspend") })
                if (sddm.canHibernate) m.push({ key: "hibernate", icon: "hibernate", text: root.tr("Hibernate") })
                m.push({ key: "reboot", icon: "restart", text: root.tr("Restart"), enabled: sddm.canReboot })
                m.push({ key: "poweroff", icon: "power", text: root.tr("Shut Down"), enabled: sddm.canPowerOff })
                return m
            }
            items: actions
            onPicked: function(i) {
                var key = actions[i].key
                menus.open = ""
                if (key === "suspend") sddm.suspend()
                else if (key === "hibernate") sddm.hibernate()
                else if (key === "reboot") sddm.reboot()
                else sddm.powerOff()
            }
        }
    }

    function languageName(code) {
        if (code === "") return tr("Language")
        for (var i = 0; i < languages.length; i++) if (languages[i].code === code) return languages[i].name
        return code
    }

    // ------------------------------------------------------------ on-screen keyboard
    // Qt Virtual Keyboard is optional: when its QML module is missing the
    // loader fails quietly and the menu says "Not installed".
    Loader {
        id: osk
        property bool shown: false
        property bool available: status === Loader.Ready
        source: "VirtualKeyboard.qml"
        anchors.left: parent.left; anchors.right: parent.right
        y: shown ? parent.height - height : parent.height
        z: 20
        visible: shown && available
        Behavior on y { NumberAnimation { duration: 160 } }
    }

    Keys.onEscapePressed: menus.open = ""

    Component.onCompleted: {
        loadLanguage()
        Qt.callLater(function() {
            pickInitialUser()
            if (root.manualUser && userField.text.length === 0) userField.forceActiveFocus()
            else password.forceActiveFocus()
        })
    }
}
