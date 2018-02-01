import _ from 'underscore';

import ItemModel from 'girder/models/ItemModel';
import { restRequest } from 'girder/rest';

var IqrSessionModel = ItemModel.extend({
    altUrl: 'smqtk_iqr/session',

    // This is adapted from girder.models.MetadataMixin
    // It needs to be copied because we want to update the IQR session metadata
    // which needs to be updated at item/:id/metadata instead of smqtk_iqr/session/:id/metadata
    _sendMetadata: function (metadata, successCallback, errorCallback) {
        restRequest({
            path: this.resourceName + '/' + this.get('_id') + '/metadata',
            contentType: 'application/json',
            data: JSON.stringify(metadata),
            type: 'PUT',
            error: null
        }).done((resp) => {
            this.set('meta', resp.meta);
            if (_.isFunction(successCallback)) {
                successCallback();
            }
        }).error((err) => {
            err.message = err.responseJSON.message;
            if (_.isFunction(errorCallback)) {
                errorCallback(err);
            }
        });
    },

    addPositiveUuid: function (uuid, done) {
        var pos_uuids = this.get('meta').pos_uuids || [],
            neg_uuids = this.get('meta').neg_uuids || [];

        this.get('meta').pos_uuids = _.union(pos_uuids, [uuid]);
        this.get('meta').neg_uuids = _.difference(neg_uuids, [uuid]);

        this._sendMetadata(this.get('meta'), done);
    },

    removePositiveUuid: function (uuid, done) {
        var pos_uuids = this.get('meta').pos_uuids || [];

        this.get('meta').pos_uuids = _.difference(pos_uuids, [uuid]);
        this._sendMetadata(this.get('meta'), done);
    },

    addNegativeUuid: function (uuid, done) {
        var pos_uuids = this.get('meta').pos_uuids || [],
            neg_uuids = this.get('meta').neg_uuids || [];

        this.get('meta').pos_uuids = _.difference(pos_uuids, [uuid]);
        this.get('meta').neg_uuids = _.union(neg_uuids, [uuid]);

        this._sendMetadata(this.get('meta'), done);
    },

    removeNegativeUuid: function (uuid, done) {
        var neg_uuids = this.get('meta').neg_uuids || [];

        this.get('meta').neg_uuids = _.difference(neg_uuids, [uuid]);
        this._sendMetadata(this.get('meta'), done);
    }
});

export default IqrSessionModel;
