/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.CountryPhoneCodeHandler = publicWidget.Widget.extend({
    selector: '.contact_country', // Selector for the country dropdown

    events: {
        'change': '_onCountryChange',
    },

    /**
     * Dynamically retrieves the phone input field.
     */
    _getPhoneField() {
        return document.querySelector('.phone_custom'); // Query phone input field dynamically
    },

    /**
     * Triggered when the country dropdown changes.
     */
    async _onCountryChange(event) {
        const countryId = event.target.value; // Get selected country ID
        const phoneField = this._getPhoneField(); // Dynamically get phone field

        if (!phoneField) {
            console.error("Phone field (.phone_custom) not found during country change.");
            return;
        }
        if (!countryId) {
            phoneField.value = ''; // Clear phone field if no country selected
            return;
        }

        try {
            // Fetch country info
            const response = await rpc(`/website/country_infos/${parseInt(countryId)}`);

            if (response && response.phone_code) {
                phoneField.value = `+${response.phone_code}`;

                // Attach or remove validation based on country
                this._attachPhoneValidation(phoneField, response);
            } else {
                console.warn("No phone code found for the selected country.");
                phoneField.value = '';
            }
        } catch (error) {
            console.error("Error fetching country phone code:", error);
        }
    },

    /**
     * Attaches phone number validation if the country is Saudi Arabia.
     * Removes validation for other countries.
     */
    _attachPhoneValidation(phoneField, countryInfo) {
        // Remove existing input listener
        phoneField.removeEventListener('input', this._validatePhoneNumber.bind(this));

        if (countryInfo.country_name === 'Saudi Arabia' || countryInfo.country_id === 'SA') {
            // Add validation listener for Saudi Arabia
            phoneField.addEventListener('input', this._validatePhoneNumber.bind(this, phoneField, countryInfo.phone_code));
        } else {
            // Clear any validation for other countries
            phoneField.setCustomValidity('');
        }
    },

    /**
     * Validates the phone number for Saudi Arabia.
     * Ensures the number (excluding the country code) does not exceed 9 digits.
     */
    _validatePhoneNumber(phoneField, phoneCode, event) {
        const phoneNumber = phoneField.value.replace(`+${phoneCode}`, '').trim(); // Extract the number after the country code

        if (phoneNumber.length <= 9) {
            phoneField.setCustomValidity(''); // Clear error if valid
        } else {
            phoneField.setCustomValidity('Phone number must not exceed 9 digits after the country code.');
        }
    },
});
