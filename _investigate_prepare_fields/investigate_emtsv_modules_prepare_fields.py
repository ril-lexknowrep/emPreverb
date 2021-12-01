
#### https://raw.githubusercontent.com/nytud/HunTag3/master/HunTag3/HunTag3.py

    def prepare_fields(self, field_names):
        #target_fields_len = len(self.target_fields)
        #if target_fields_len != 1:
        #    print('ERROR: Wrong number of target fields are specified ({0})! '
        #          'TAGGING REQUIRES ONLY ONE TAG FIELD!'.
        #          format(target_fields_len), file=sys.stderr, flush=True)
        #    sys.exit(1)
        self._tag_field = field_names[self.target_fields[0]]
        return bind_features_to_indices(self.features, self._tag_field, field_names)

    def bind_features_to_indices(features, tag_field, field_names):
        name_dict = {k: v for k, v in field_names.items() if k != tag_field and v != tag_field}
        for name, feature in features.items():
            feature.field_indices = [name_dict[f] for f in feature.fields]
        return features

#### https://raw.githubusercontent.com/vadno/emconll/master/emconll/emconll.py

    def prepare_fields(self, field_names):
        """
        Map the mandatory emtsv field names to the CoNLL names tied to the current indices
        :param field_names: emtsv header
        :return: (list) The "mapping" of the mandatory CoNLL field names to the current indices
        """

        fields_nums = [field_names.get(emtsv_name, '_') for emtsv_name in self._col_mapper.keys()]
        if self._add_space_after_no and fields_nums[9] == '_' and field_names.get('wsafter') is not None:
            self._add_space_after_no_fun = self._add_space_after_no_real_fun
            self._ws_after_column_no = field_names['wsafter']
        if self._force_id and fields_nums[0] == '_':
            self._add_id = self._add_id_fun

        return fields_nums

#### https://raw.githubusercontent.com/vadno/emzero/master/emzero/emzero.py

    # all fields in the '"form" -> 0' direction
    def prepare_fields(self, field_names):
        return {k: v for k, v in field_names.items() if isinstance(k, str)}, field_names['id']

#### https://raw.githubusercontent.com/nytud/emIOBUtils/master/emIOBUtils/emIOBUtils.py

    # hack to handle any input fields
    def prepare_fields(self, field_names):
        return [field_names[next(iter(self.source_fields))]]

==========

# XXX maybe it is not a good idea to hardcode here the name of the features -- INDEED!
# a solution: take all input fields

#### https://raw.githubusercontent.com/nytud/emmorphpy/master/emmorphpy/emmorphpy.py
#### https://raw.githubusercontent.com/nytud/hunspellpy/master/hunspellpy/hunspellpy.py
    def prepare_fields(self, field_names):
        return [field_names['form']]

#### https://raw.githubusercontent.com/nytud/purepospy/master/purepospy/purepospy.py
    def prepare_fields(self, field_names):
        return [field_names['form'], field_names['anas']]

#### https://raw.githubusercontent.com/nytud/emterm/master/emterm/emterm.py
    def prepare_fields(self, field_names):
        return [field_names['form'], field_names['lemma']]

#### https://raw.githubusercontent.com/nytud/emconspy/master/emconspy/emconspy.py
#### https://raw.githubusercontent.com/vadno/emmorph2ud2/master/emmorph2ud2/emmorph2ud2.py
#### https://raw.githubusercontent.com/vadno/emmorph2ud/master/emmorph2ud/emmorph2ud.py
    def prepare_fields(self, field_names):
        return [field_names['form'], field_names['lemma'], field_names['xpostag']]

#### https://raw.githubusercontent.com/nytud/emdeppy/master/emdeppy/emdeppy.py
    def prepare_fields(self, field_names):
        return [field_names['form'], field_names['lemma'], field_names['upostag'], field_names['feats']]

==========

# XXX these needed by name for the decoding <- what is "decoding"?

#### https://raw.githubusercontent.com/nytud/emudpipe/master/emudpipe/emudpipe.py
#### https://raw.githubusercontent.com/nytud/emdummy/master/emdummy/emdummy.py
#### https://raw.githubusercontent.com/nytud/emgateconv/master/emgateconv/emgateconv.py
#### https://raw.githubusercontent.com/ELTE-DH/emstanza/master/emstanza/emstanza.py
    def prepare_fields(self, field_names):
        return field_names

