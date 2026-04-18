from rest_framework import serializers


class RunOnceSerializer(serializers.Serializer):
    prompt = serializers.CharField()
    provider = serializers.ChoiceField(choices=["openai", "baseten"])
    openai_model = serializers.CharField(required=False, default="gpt-4o-mini")
    system = serializers.CharField(required=False, allow_blank=True, default="")
    temperature = serializers.FloatField(required=False, default=0.2)
    max_tokens = serializers.IntegerField(required=False, default=1024)


class RunSuiteSerializer(serializers.Serializer):
    suite_id = serializers.CharField(required=False, default="default")
    providers = serializers.ListField(
        child=serializers.ChoiceField(choices=["openai", "baseten"]),
        required=False,
        allow_empty=False,
    )
    openai_model = serializers.CharField(required=False, default="gpt-4o-mini")
    system = serializers.CharField(required=False, allow_blank=True, default="")
    temperature = serializers.FloatField(required=False, default=0.2)
    max_tokens = serializers.IntegerField(required=False, default=1024)
    use_judge = serializers.BooleanField(required=False, default=True)
    judge_model = serializers.CharField(required=False, default="gpt-4o-mini")
