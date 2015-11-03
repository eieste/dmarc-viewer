from django.utils.translation import gettext as _

from django.forms import ModelForm, ValidationError, ChoiceField, MultipleChoiceField, TypedMultipleChoiceField, \
    CharField, GenericIPAddressField, IntegerField, DateTimeField, TypedChoiceField, BooleanField
from django.forms.models import inlineformset_factory, modelform_factory

from django.forms.widgets import RadioSelect, Textarea

from myDmarcApp.models import Report, Reporter, ReportError, Record, \
    PolicyOverrideReason, AuthResultDKIM, AuthResultSPF, View, FilterSet, ReportType, \
    DateRange, ReportSender, ReportReceiverDomain, \
    SourceIP, RawDkimDomain, RawDkimResult, RawSpfDomain, RawSpfResult, \
    AlignedDkimResult, AlignedSpfResult, Disposition, MultipleDkim
from myDmarcApp.widgets import ColorPickerWidget, MultiSelectWidget, DatePickerWidget
import choices

class ViewForm(ModelForm):

    class Meta:
        model = View
        fields = ['title', 'description', 'enabled', 'type_map', 'type_table', 'type_line']
        labels = {
            "enabled": _("Show in sidebar"),
        }
        widgets = {
            'description': Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super(ViewForm, self).__init__(*args, **kwargs)
        self.fields["report_type"] = ChoiceField(label="Report Type", choices=choices.REPORT_TYPE, required=True)

        # Initialize all fields for date range
        self.fields["dr_type"]     = TypedChoiceField(label="Date Range Type", choices=choices.DATE_RANGE_TYPE, coerce=int, widget=RadioSelect())
        self.fields["quantity"]    = IntegerField(label="Quantity", required=False)
        self.fields["unit"]        = TypedChoiceField(label="Unit", coerce=int, choices=choices.TIME_UNIT, required=False)
        self.fields["begin"]       = DateTimeField(label="Report Date Begin", required=False, widget=DatePickerWidget())
        self.fields["end"]         = DateTimeField(label="Report Date End", required=False, widget=DatePickerWidget())

        # Set default for date range type
        self.fields["dr_type"].initial = choices.DATE_RANGE_TYPE_FIXED

        # If this form is already bound to a view, add the data from the model
        if self.instance.id:
            for date_range in DateRange.objects.filter(foreign_key=self.instance.id):
                self.fields["dr_type"].initial     = date_range.dr_type

                self.fields["unit"].initial        = date_range.unit
                self.fields["quantity"].initial    = date_range.quantity
                if date_range.begin:
                    self.fields["begin"].initial   = date_range.begin.strftime('%Y-%m-%d')
                if date_range.end:
                    self.fields["end"].initial     = date_range.end.strftime('%Y-%m-%d')

            for report_type in ReportType.objects.filter(foreign_key=self.instance.id):
                self.fields["report_type"].initial  = report_type.value

    def clean(self):
        cleaned_data    = super(ViewForm, self).clean()
        dr_type         = cleaned_data.get("dr_type")
        begin           = cleaned_data.get("begin")
        end             = cleaned_data.get("end")
        quantity        = cleaned_data.get("quantity")
        unit            = cleaned_data.get("unit")

        # Only one of both pairs (fixed or variable) should ever be specified
        only_one_msg = _('Specify either fixed or variable time range!')
        if (((dr_type == choices.DATE_RANGE_TYPE_FIXED) and
            (unit or quantity)) or
            ((dr_type == choices.DATE_RANGE_TYPE_VARIABLE) and
            (begin or end))):
                self.add_error('begin', ValidationError(only_one_msg, code='required'))
                self.add_error('end', ValidationError(only_one_msg, code='required'))
                self.add_error('unit', ValidationError(only_one_msg, code='required'))
                self.add_error('quantity', ValidationError(only_one_msg, code='required'))

        # If the user wants fixed ranges begin and end must be specified
        required_msg = _('This field is required.')
        if dr_type == choices.DATE_RANGE_TYPE_FIXED:
            if not begin:
                self.add_error('begin', ValidationError(required_msg, code='required'))
            if not end:
                self.add_error('end', ValidationError(required_msg, code='required'))

        # Ff the user wants variable ranges unit and quantity must be specified
        if dr_type == choices.DATE_RANGE_TYPE_VARIABLE:
            if not unit:
                self.add_error('unit', ValidationError(required_msg, code='required'))
            if not quantity:
                self.add_error('quantity', ValidationError(required_msg, code='required'))

        return cleaned_data

    def save(self):
        view_instance = super(ViewForm, self).save()
        
        # This is actually a one-to-one relationship but modeled with fk (m2o)
        date_range = DateRange.objects.filter(foreign_key=self.instance.id).first()
        if not date_range:
            date_range = DateRange(foreign_key=self.instance)
        date_range.dr_type  = self.cleaned_data["dr_type"]
        date_range.unit     = self.cleaned_data["unit"] or None
        date_range.quantity = self.cleaned_data["quantity"]
        date_range.begin    = self.cleaned_data["begin"]
        date_range.end      = self.cleaned_data["end"]

        date_range.save()

        # This is actually a one-to-one relationship but modeled with fk (m2o)
        report_type = ReportType.objects.filter(foreign_key=self.instance.id).first()
        if not report_type:
            report_type = ReportType(foreign_key=self.instance)
        report_type.value = self.cleaned_data["report_type"]
        report_type.save()

        return view_instance


class FilterSetForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FilterSetForm, self).__init__(*args, **kwargs)
        self.additional_filter_fields = {
            "report_sender"              : {"choices" : Reporter.objects.distinct().values_list('email', 'email'), 
                                            "label"   : "Report Sender", 
                                            "class"   : ReportSender,
                                            "type"    : unicode},
            "report_receiver_domain"     : {"choices" : Report.objects.distinct().values_list('domain', 'domain'), 
                                            "label"   : "Report Receiver Domain", 
                                            "class"   : ReportReceiverDomain,
                                            "type"    : unicode},
            "raw_dkim_domain"            : {"choices" : AuthResultDKIM.objects.distinct().values_list('domain', 'domain'), 
                                            "label"   : "Raw DKIM Domain", 
                                            "class"   : RawDkimDomain,
                                            "type"    : unicode},
            "raw_spf_domain"             : {"choices" : AuthResultSPF.objects.distinct().values_list('domain', 'domain'), 
                                            "label"   : "Raw SPF Domain", 
                                            "class"   : RawSpfDomain,
                                            "type"    : unicode},
            "raw_dkim_result"            :  {"choices" : choices.DKIM_RESULT, 
                                            "label"   : "Raw DKIM Result", 
                                            "class"   : RawDkimResult,
                                            "type"    : int},
            "raw_spf_result"             : {"choices" : choices.SPF_RESULT, 
                                            "label"   : "Raw SPF Result", 
                                            "class"   : RawSpfResult,
                                            "type"    : int},
            "aligned_dkim_result"        : {"choices" : choices.DMARC_RESULT, 
                                            "label"   : "Aligned DKIM Result", 
                                            "class"   : AlignedDkimResult,
                                            "type"    : int},
            "aligned_spf_result"         : {"choices" : choices.DMARC_RESULT, 
                                            "label"   : "Aligned SPF Result", 
                                            "class"   : AlignedSpfResult,
                                            "type"    : int},
            "disposition"                : {"choices" : choices.DISPOSITION_TYPE, 
                                            "label"   : "Disposition", 
                                            "class"   : Disposition,
                                            "type"    : int}
            }
        # Initialize additional multiple choice filter set fields.
        for field_name, field_dict in self.additional_filter_fields.iteritems():

            # Creating a typed choice field helps performing built in form clean magic
            self.fields[field_name]  = TypedMultipleChoiceField(coerce=field_dict["type"], required=False, label=field_dict["label"], choices=field_dict["choices"], widget=MultiSelectWidget)
            if self.instance.id:
                self.fields[field_name].initial = field_dict["class"].objects.filter(foreign_key=self.instance.id).values_list('value', flat=True)

         # These are extra because they are one-to-one ergo no MultipleChoiceField
        self.fields["source_ip"]     =  GenericIPAddressField(required=False, label='Mail Sender IP')
        self.fields["multiple_dkim"] =  BooleanField(required=False, label='Multiple DKIM only')

        if self.instance.id:
            source_ip_initial     = SourceIP.objects.filter(foreign_key=self.instance.id).values_list('value', flat=True)
            if len(source_ip_initial):
                self.fields['source_ip'].initial = source_ip_initial[0]
            multiple_dkim_initial = MultipleDkim.objects.filter(foreign_key=self.instance.id).values_list('value', flat=True)
            if len(multiple_dkim_initial):
                self.fields["multiple_dkim"].initial = multiple_dkim_initial[0]

    def save(self, commit=True):
        instance = super(FilterSetForm, self).save()

        # Add new many-to-one filter fields to a filter set object
        # remove existing if removed in form 
        for field_name, field_dict in self.additional_filter_fields.iteritems():
            existing_filters = field_dict["class"].objects.filter(foreign_key=self.instance.id).values_list('value', flat=True)
            for filter_value in field_dict["choices"]:
                # We need the first choices tuple, because this is stored in the db and refers to form values (cleaned data)
                filter_value = filter_value[0]
                if filter_value not in existing_filters and filter_value in self.cleaned_data[field_name]:
                    new_filter = field_dict["class"]()
                    new_filter.foreign_key = self.instance
                    new_filter.value = filter_value
                    new_filter.save()
                if filter_value in existing_filters and filter_value not in self.cleaned_data[field_name]:
                    field_dict["class"].objects.filter(foreign_key=self.instance.id, value=filter_value).delete()

        #  update, create or delete source_ip
        source_ip       = SourceIP.objects.filter(foreign_key=self.instance.id).first()
        source_ip_value = self.cleaned_data["source_ip"]
        if source_ip and not source_ip_value:
            source_ip.delete()

        if not source_ip and source_ip_value:
            source_ip = SourceIP(foreign_key=self.instance, value = source_ip_value)
            source_ip.save()

        if source_ip and source_ip_value:
            source_ip.value = source_ip_value
            source_ip.save()

        # delete or create multiple dkim only 
        # we don't have to update because we keep only true valued instances
        multiple_dkim       = MultipleDkim.objects.filter(foreign_key=self.instance.id).first()
        multiple_dkim_value = self.cleaned_data["multiple_dkim"]
        if multiple_dkim and not multiple_dkim_value:
            multiple_dkim.delete()
        if not multiple_dkim and multiple_dkim_value:
            multiple_dkim = MultipleDkim(foreign_key=self.instance, value=multiple_dkim_value)
            multiple_dkim.save()

        return instance

    class Meta:
        model = FilterSet
        fields = ['label', 'color']
        widgets = {'color': ColorPickerWidget}

FilterSetFormSet                    = inlineformset_factory(View, FilterSet, form=FilterSetForm, can_delete=True, extra=0)