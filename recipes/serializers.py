from rest_framework import serializers
from .models import Recipe, Ingredient, Instruction

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['text']

class InstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instruction
        fields = ['text', 'order']

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    instructions = InstructionSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'image', 'time', 'servings', 'difficulty',
                 'chef', 'category', 'description', 'ingredients', 'instructions']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        instructions_data = validated_data.pop('instructions')
        recipe = Recipe.objects.create(**validated_data)
        
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)
        
        for idx, instruction_data in enumerate(instructions_data, 1):
            instruction_data['order'] = idx
            Instruction.objects.create(recipe=recipe, **instruction_data)
        
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        instructions_data = validated_data.pop('instructions', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.ingredients.all().delete()
        instance.instructions.all().delete()

        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=instance, **ingredient_data)

        for idx, instruction_data in enumerate(instructions_data, 1):
            instruction_data['order'] = idx
            Instruction.objects.create(recipe=instance, **instruction_data)

        return instance