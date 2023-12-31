odoo.define('pos_hr_mobile.LoginScreen', function (require) {
    "use strict";

    const Registries = require('point_of_sale.Registries');
    const LoginScreen = require('pos_hr.LoginScreen');
    const BarcodeScanner = require('@web_enterprise/webclient/barcode/barcode_scanner')[Symbol.for("default")];;

    const LoginScreenMobile = LoginScreen => class extends LoginScreen {
        constructor() {
            super(...arguments);
            this.hasMobileScanner = BarcodeScanner.isBarcodeScannerSupported();
        }

        async open_mobile_scanner() {
            let data;
            try {
                data = await BarcodeScanner.scanBarcode();
            } catch (error) {
                if (error.error && error.error.message) {
                    // Here, we know the structure of the error raised by BarcodeScanner.
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Unable to scan'),
                        body: error.error.message,
                    });
                    return;
                }
                // Just raise the other errors.
                throw error;
            }
            if (data) {
                this.env.pos.barcode_reader.scan(data);
                if ('vibrate' in window.navigator) {
                    window.navigator.vibrate(100);
                }
            } else {
                this.env.services.notification.notify({
                    type: 'warning',
                    message: 'Please, Scan again !',
                });
            }
        }
    };
    Registries.Component.extend(LoginScreen, LoginScreenMobile);

    return LoginScreen;
});
