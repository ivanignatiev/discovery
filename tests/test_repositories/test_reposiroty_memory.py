def test_repository_memory():
    from discovery.repository import MemoryRepository

    repository = MemoryRepository()
    assert repository.get_all() == {}

    repository.add('resource_type_1', 'item')
    resources = repository.get_all()

    assert resources.get('resource_type_1') == ['item']
    assert repository.get_all_by_type('resource_type_1') == ['item']
    assert repository.get_all_by_type('resource_type_2') == []